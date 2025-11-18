"""This module defines test fixtures."""

from fastapi.testclient import TestClient
import pytest

from apps.api_server import grocery


@pytest.fixture
def test_client() -> TestClient:
    """Defines a pytest fixture for the FastAPI server application."""
    fastapi_app = grocery.app

    testing_client = TestClient(fastapi_app)

    return testing_client
