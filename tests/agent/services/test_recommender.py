"""Unit tests for recommender.py"""

import json

import tenacity

from apps.agent.dependencies import constants
from apps.agent.models import models
from apps.agent.services import recommender as r


def test_recommend_products_success(mocked_openai_client, mocker, tmp_path):
    """Test that recommend_products() returns product recommendations if there are no errors."""
    expected = models.LLMRecommendationList(
        recommendations=[
            models.LLMRecommendationListPerGroceryListLine(
                query="1 bag of sugar", suggestions=[]
            )
        ]
    )

    recommender = r.RecommenderService(
        api_key="fake-key",
        model_name=constants.RECOMMENDER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )
    mocked_openai_client.return_value.request_structured_response.return_value = (
        expected
    )

    result = recommender.recommend_products(
        models.PrunedCatalogList(
            lines=[
                models.PrunedCatalogPerGroceryListLine(
                    query="1 bag of sugar",
                    product="sugar",
                    quantity=1.0,
                    unit="bag",
                    candidates=[],
                )
            ]
        )
    )

    assert isinstance(result, models.LLMRecommendationList)
    assert result == expected


def test_recommend_products_failure(mocked_openai_client, mocker, tmp_path):
    """Test that recommend_products() returns None if there are errors."""
    recommender = r.RecommenderService(
        api_key="fake-key",
        model_name=constants.RECOMMENDER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )
    mocked_openai_client.return_value.request_structured_response.side_effect = (
        tenacity.RetryError(mocker.Mock())
    )

    result = recommender.recommend_products(mocker.Mock())

    assert result is None


def test_return_mocked_response_success(mocker, tmp_path):
    """Test that return_mocked_response() returns the mocked response written in a file."""
    content = {"recommendations": [{"query": "1 bag of sugar", "suggestions": []}]}

    file = tmp_path / "list01.txt"
    file.write_text(json.dumps(content))

    recommender = r.RecommenderService(
        api_key=None,
        model_name=constants.RECOMMENDER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = recommender.return_mocked_response("list01.txt")

    assert isinstance(result, models.LLMRecommendationList)
    assert result.recommendations[0].query == "1 bag of sugar"


def test_return_mocked_response_missing_file(mocker, tmp_path):
    """Test that return_mocked_response() returns None on a file not found error."""
    recommender = r.RecommenderService(
        api_key=None,
        model_name=constants.RECOMMENDER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = recommender.return_mocked_response("does_not_exist.txt")

    assert result is None


def test_return_mocked_response_invalid_json(mocker, tmp_path):
    """Test that return_mocked_response() returns None on an invalid JSON error."""
    file = tmp_path / "bad.txt"
    file.write_text("{invalid json}")

    recommender = r.RecommenderService(
        api_key=None,
        model_name=constants.RECOMMENDER_LLM_MODEL,
        base_prompt_file=mocker.Mock(),
        dummy_responses_folder=tmp_path,
        logger=mocker.Mock(),
    )

    result = recommender.return_mocked_response("bad.txt")

    assert result is None
