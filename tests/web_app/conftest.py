"""This module defines test fixtures."""
import flask.testing
import pytest
from apps.web_app import file_uploader


@pytest.fixture
def test_client() -> flask.testing.FlaskClient:
    """ Defines a pytest fixture for Flask web application. """
    flask_app = file_uploader.app

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    # start testing
    yield testing_client

    ctx.pop()
