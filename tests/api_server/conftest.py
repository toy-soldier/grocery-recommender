"""This module defines test fixtures."""

import pytest

from fastapi.testclient import TestClient

from apps.api_server import grocery
from apps.api_server.dependencies import constants, database, scripts


@pytest.fixture
def test_client() -> TestClient:
    """Defines a pytest fixture for the FastAPI server application."""
    fastapi_app = grocery.app
    testing_client = TestClient(fastapi_app)
    return testing_client


@pytest.fixture(scope="session", autouse=True)
def patch_global_engine() -> None:
    """Patch the module-level engine to use an in-memory SQLite DB."""
    test_engine = database.get_engine(
        database_uri=constants.SQLITE_URI.format(":memory:")
    )
    scripts.create(test_engine)
    scripts.seed(test_engine, 17)

    database.engine = test_engine
    return None
