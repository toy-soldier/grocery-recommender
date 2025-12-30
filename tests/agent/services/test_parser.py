"""Unit tests for parser.py"""

import json

import tenacity

from apps.agent.dependencies import constants
from apps.agent.models import models
from apps.agent.services import parser as p


def test_parse_grocery_text_success(mocked_openai_client, mocker, tmp_path):
    """Test that parse_grocery_text() returns the parsed grocery text if there are no errors."""
    expected = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(
                query="3 packs of milk",
                product="milk",
                quantity=3,
                unit="packs",
            )
        ]
    )

    parser = p.ParserService(
        api_key="fake-key",
        model_name=constants.PARSER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )
    mocked_openai_client.return_value.request_structured_response.return_value = (
        expected
    )

    result = parser.parse_grocery_text("3 packs of milk")

    assert isinstance(result, models.ParsedGroceryList)
    assert result == expected


def test_parse_grocery_text_failure(mocked_openai_client, mocker, tmp_path):
    """Test that parse_grocery_text() returns None if there are errors."""
    parser = p.ParserService(
        api_key="fake-key",
        model_name=constants.PARSER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )
    mocked_openai_client.return_value.request_structured_response.side_effect = (
        tenacity.RetryError(mocker.Mock())
    )

    result = parser.parse_grocery_text("milk")

    assert result is None


def test_return_mocked_response_success(mocker, tmp_path):
    """Test that return_mocked_response() returns the mocked response written in a file."""
    content = {
        "grocery_list": [
            {"query": "milk", "product": "milk", "quantity": None, "unit": None}
        ]
    }

    file = tmp_path / "list01.txt"
    file.write_text(json.dumps(content))

    parser = p.ParserService(
        api_key=None,
        model_name=constants.PARSER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = parser.return_mocked_response("list01.txt")

    assert isinstance(result, models.ParsedGroceryList)
    assert result.grocery_list[0].product == "milk"


def test_return_mocked_response_missing_file(mocker, tmp_path):
    """Test that return_mocked_response() returns None on a file not found error."""
    parser = p.ParserService(
        api_key=None,
        model_name=constants.PARSER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = parser.return_mocked_response("does_not_exist.txt")

    assert result is None


def test_return_mocked_response_invalid_json(mocker, tmp_path):
    """Test that return_mocked_response() returns None on an invalid JSON error."""
    file = tmp_path / "bad.txt"
    file.write_text("{invalid json}")

    parser = p.ParserService(
        api_key=None,
        model_name=constants.PARSER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = parser.return_mocked_response("bad.txt")

    assert result is None
