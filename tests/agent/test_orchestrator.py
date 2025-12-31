"""Unit tests for orchestrator.py"""

from apps.agent import orchestrator
from apps.agent.models import models


def test_main(mocker):
    """Test that main() calls the agent initializer and calls process()."""
    mocked_init = mocker.patch("apps.agent.orchestrator.init_agent")
    orchestrator.main()
    assert mocked_init.call_count == 1
    mocked_process = mocked_init.return_value.process
    assert mocked_process.call_count == 1


def test_init_agent(
    mocker,
    mocked_parser_service,
    mocked_recommender_service,
    mocked_inventory_service,
    mocked_fuzzy_service,
):
    """
    Since this function can be called by main() or the web application,
    ensure that init_agent() indeed initializes the agent.
    """
    mocker.patch("apps.agent.orchestrator.logging")
    obj = orchestrator.init_agent()
    assert mocked_parser_service.call_count == 1
    assert mocked_recommender_service.call_count == 1
    assert mocked_inventory_service.call_count == 1
    assert mocked_fuzzy_service.call_count == 1
    assert isinstance(obj, orchestrator.GroceryAgent)
    mocked_load = mocked_inventory_service.return_value.load_catalog
    assert mocked_load.call_count == 1


def test_process_on_empty_catalog(
    mocker,
    mocked_parser_service,
    mocked_recommender_service,
    mocked_inventory_service,
    mocked_fuzzy_service,
):
    """Test that process() returns empty recommendations for an empty catalog."""
    mocker.patch("apps.agent.orchestrator.logging")
    empty = models.ProductCatalog(catalog=[])
    mocked_inventory_service.return_value = mocker.Mock(catalog=empty)
    obj = orchestrator.init_agent()
    resp = obj.process("some.file", "some text")
    assert resp == {"recommendations": []}


def test_process_on_api_key_existence(
    mocker,
    mocked_parser_service,
    mocked_recommender_service,
    mocked_inventory_service,
    mocked_fuzzy_service,
):
    """Test that process() calls the correct methods depending on the API key existence."""
    mocked_use_llms = mocker.patch("apps.agent.orchestrator.GroceryAgent._use_llms")
    mocked_mock_llms = mocker.patch("apps.agent.orchestrator.GroceryAgent._mock_llms")

    obj = orchestrator.GroceryAgent(
        mocked_parser_service,
        mocked_recommender_service,
        mocked_inventory_service,
        mocked_fuzzy_service,
        api_key="some key",
        logger=mocker.Mock(),
    )
    obj.process("some.file", "some text")
    assert mocked_use_llms.call_count == 1
    assert mocked_mock_llms.call_count == 0

    obj = orchestrator.GroceryAgent(
        mocked_parser_service,
        mocked_recommender_service,
        mocked_inventory_service,
        mocked_fuzzy_service,
        api_key=None,
        logger=mocker.Mock(),
    )
    obj.process("some.file", "some text")
    assert mocked_use_llms.call_count == 1
    assert mocked_mock_llms.call_count == 1


def test_mock_llms_on_empty_responses(
    mocker,
    mocked_parser_service,
    mocked_recommender_service,
    mocked_inventory_service,
    mocked_fuzzy_service,
):
    """Test that _mock_llms() returns empty recommendations for empty responses."""
    mocker.patch("apps.agent.orchestrator.logging")
    empty = models.LLMRecommendationList(recommendations=[])
    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp != empty

    mocked_parser_service.return_value.return_mocked_response.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp == empty
    mocked_parser_service.return_value.return_mocked_response.return_value = (
        mocker.Mock()
    )

    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp != empty

    mocked_recommender_service.return_value.return_mocked_response.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp == empty
    mocked_recommender_service.return_value.return_mocked_response.return_value = (
        mocker.Mock()
    )

    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp != empty

    mocked_parser_service.return_value.return_mocked_response.return_value = None
    mocked_recommender_service.return_value.return_mocked_response.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._mock_llms("some.file")
    assert resp == empty


def test_use_llms_on_empty_responses(
    mocker,
    mocked_parser_service,
    mocked_recommender_service,
    mocked_inventory_service,
    mocked_fuzzy_service,
):
    """Test that _use_llms() returns empty recommendations for empty responses."""
    mocker.patch("apps.agent.orchestrator.logging")
    mocker.patch("apps.agent.models.models.CatalogForFuzzyMatching")
    empty = models.LLMRecommendationList(recommendations=[])
    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp != empty

    mocked_parser_service.return_value.parse_grocery_text.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp == empty
    mocked_parser_service.return_value.parse_grocery_text.return_value = mocker.Mock()

    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp != empty

    mocked_fuzzy_service.return_value.filter_catalog.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp == empty
    mocked_fuzzy_service.return_value.filter_catalog.return_value = mocker.Mock()

    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp != empty

    mocked_recommender_service.return_value.recommend_products.return_value = None
    obj = orchestrator.init_agent()
    resp = obj._use_llms("some text")
    assert resp == empty
