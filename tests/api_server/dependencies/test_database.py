"""Unit tests for database.py"""

from apps.api_server.dependencies import database


def test_compute_database_uri():
    """Unit test for compute_database_uri()."""
    database_uri = database.compute_database_uri()
    assert database_uri.startswith("sqlite:///")
    assert database_uri.endswith("inventory.sqlite3")


def test_get_engine(mocker):
    """Unit test for get_engine()."""
    mocked_create_engine = mocker.patch(
        "apps.api_server.dependencies.database.create_engine"
    )
    database.get_engine(None)
    assert mocked_create_engine.call_count == 1


def test_get_session(mocker):
    mocked_get_engine = mocker.patch("apps.api_server.dependencies.database.get_engine")
    mocked_get_engine.return_value = "test"

    generated_session = list(database.get_session())[0]
    assert str(generated_session.get_bind().url) == "sqlite:///:memory:"

    mocker.patch.object(database, "engine", None)
    generated_session = list(database.get_session())[0]
    assert generated_session.get_bind() == "test"
