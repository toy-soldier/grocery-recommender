"""This module defines test fixtures."""

import unittest

import pytest
import pytest_mock


@pytest.fixture
def mocked_get(mocker: pytest_mock.plugin.MockerFixture) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.clients.api_client.requests.get")


@pytest.fixture
def mocked_api_client(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.inventory.api_client.APIClient")


@pytest.fixture
def mocked_openai(mocker: pytest_mock.plugin.MockerFixture) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.clients.openai_client.openai.OpenAI")


@pytest.fixture
def mocked_openai_client(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.base_llm.openai_client.OpenAIClient")


@pytest.fixture
def mocked_parser_service(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.parser.ParserService")


@pytest.fixture
def mocked_recommender_service(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.recommender.RecommenderService")


@pytest.fixture
def mocked_inventory_service(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.inventory.InventoryService")


@pytest.fixture
def mocked_fuzzy_service(
    mocker: pytest_mock.plugin.MockerFixture,
) -> unittest.mock.MagicMock:
    return mocker.patch("apps.agent.services.fuzzy_filter.FuzzyFilterService")
