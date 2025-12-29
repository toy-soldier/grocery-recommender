"""Unit tests for openai_client.py"""

import json
import openai
import pydantic
import pytest
import tenacity

from apps.agent.clients import openai_client
from apps.agent.models import models
from apps.agent.dependencies import constants


class TestRequestStringResponse:
    """These are the tests for request_string_response()"""

    def test_get_llm_response_success(self, mocker, mocked_openai):
        """Test that the client returns the LLM response."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_text_response = "Hello, this is only a test."
        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.return_value.output_text = mocked_text_response

        response = client.request_string_response("Test prompt")
        assert response == mocked_text_response
        assert mocked_function.call_count == 1

    def test_get_llm_response_raises_500(self, mocker, mocked_openai):
        """Test that the client retries when the LLM responds with an internal server error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = openai.InternalServerError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(tenacity.RetryError):
            client.request_string_response("Test prompt")
        assert mocked_function.call_count == constants.OPENAI_PLATFORM_RETRIES

    def test_get_llm_response_raises_401(self, mocker, mocked_openai):
        """Test that the client doesn't retry when the LLM responds with an authentication error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = openai.AuthenticationError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(openai.AuthenticationError):
            client.request_string_response("Test prompt")
        assert mocked_function.call_count == 1

    def test_get_llm_response_success_on_3rd_try(self, mocker, mocked_openai):
        """Test that the client returns the LLM response after two failures."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_response = mocker.Mock(output_text="Hello, this is only a test.")
        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
            mocked_response,
        )

        response = client.request_string_response("Test prompt")
        assert response == mocked_response.output_text
        assert mocked_function.call_count == 3

    def test_get_llm_response_fails_immediately_on_400(self, mocker, mocked_openai):
        """Test that the client retries, then fails immediately on a bad request."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.BadRequestError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
        )

        with pytest.raises(openai.BadRequestError):
            client.request_string_response("Test prompt")
        assert mocked_function.call_count == 2


class TestRequestJsonResponse:
    """These are the tests for request_json_response()"""

    def test_get_llm_response_success(self, mocker, mocked_openai):
        """Test that the client returns the LLM response."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_json_response = {"message": "Hello, this is only a test."}
        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.return_value.output_text = json.dumps(mocked_json_response)

        response = client.request_json_response("Test prompt")
        response = json.loads(response)
        assert response == mocked_json_response
        assert mocked_function.call_count == 1

    def test_get_llm_response_raises_500(self, mocker, mocked_openai):
        """Test that the client retries when the LLM responds with an internal server error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = openai.InternalServerError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(tenacity.RetryError):
            client.request_json_response("Test prompt")
        assert mocked_function.call_count == constants.OPENAI_PLATFORM_RETRIES

    def test_get_llm_response_raises_401(self, mocker, mocked_openai):
        """Test that the client doesn't retry when the LLM responds with an authentication error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = openai.AuthenticationError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(openai.AuthenticationError):
            client.request_json_response("Test prompt")
        assert mocked_function.call_count == 1

    def test_get_llm_response_success_on_3rd_try(self, mocker, mocked_openai):
        """Test that the client returns the LLM response after two failures."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_response = mocker.Mock(
            output_text=json.dumps({"message": "Hello, this is only a test."})
        )
        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
            mocked_response,
        )

        response = client.request_json_response("Test prompt")
        assert response == mocked_response.output_text
        assert mocked_function.call_count == 3

    def test_get_llm_response_fails_immediately_on_400(self, mocker, mocked_openai):
        """Test that the client retries, then fails immediately on a bad request."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.create
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.BadRequestError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
        )

        with pytest.raises(openai.BadRequestError):
            client.request_json_response("Test prompt")
        assert mocked_function.call_count == 2


def simulate_validation_error() -> pydantic.ValidationError:
    """A helper function to simulate a validation error."""
    try:
        models.ProductLineItem(full_name="Invalid product", sku="Invalid SKU")
    except pydantic.ValidationError as e:
        return e


class TestRequestStructuredResponse:
    """These are the tests for request_structured_response()"""

    def test_get_llm_response_success(self, mocker, mocked_openai):
        """Test that the client returns the LLM response."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_structured_response = models.ProductLineItem(
            full_name="Some product", sku=12345
        )
        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.return_value.output_parsed = mocked_structured_response

        response = client.request_structured_response(
            "Test prompt", response_model=models.ProductLineItem
        )
        assert response == mocked_structured_response
        assert mocked_function.call_count == 1

    def test_get_llm_response_fails_due_to_validation_error(
        self, mocker, mocked_openai
    ):
        """Test that the client raises a ValidationError."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())
        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.side_effect = simulate_validation_error()

        with pytest.raises(pydantic.ValidationError):
            client.request_structured_response(
                prompt="Test prompt", response_model=models.ProductLineItem
            )

        assert mocked_function.call_count == 1

    def test_get_llm_response_raises_500(self, mocker, mocked_openai):
        """Test that the client retries when the LLM responds with an internal server error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.side_effect = openai.InternalServerError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(tenacity.RetryError):
            client.request_structured_response(
                prompt="Test prompt", response_model=models.ProductLineItem
            )
        assert mocked_function.call_count == constants.OPENAI_PLATFORM_RETRIES

    def test_get_llm_response_raises_401(self, mocker, mocked_openai):
        """Test that the client doesn't retry when the LLM responds with an authentication error."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.side_effect = openai.AuthenticationError(
            message="For testing purposes", body=None, response=mocker.Mock()
        )

        with pytest.raises(openai.AuthenticationError):
            client.request_structured_response(
                prompt="Test prompt", response_model=models.ProductLineItem
            )
        assert mocked_function.call_count == 1

    def test_get_llm_response_success_on_3rd_try(self, mocker, mocked_openai):
        """Test that the client returns the LLM response after two failures."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_response = mocker.Mock(
            output_parsed=models.ProductLineItem(full_name="Some product", sku=12345)
        )
        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
            mocked_response,
        )

        response = client.request_structured_response(
            "Test prompt", response_model=models.ProductLineItem
        )
        assert response == mocked_response.output_parsed
        assert mocked_function.call_count == 3

    def test_get_llm_response_fails_immediately_on_400(self, mocker, mocked_openai):
        """Test that the client retries, then fails immediately on a bad request."""
        client = openai_client.OpenAIClient("test_key", "test_model", mocker.Mock())

        mocked_function = mocked_openai.return_value.responses.parse
        mocked_function.side_effect = (
            openai.RateLimitError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.BadRequestError(
                message="For testing purposes", body=None, response=mocker.Mock()
            ),
            openai.APIConnectionError(
                message="For testing purposes", request=mocker.Mock()
            ),
        )

        with pytest.raises(openai.BadRequestError):
            client.request_structured_response(
                "Test prompt", response_model=models.ProductLineItem
            )
        assert mocked_function.call_count == 2
