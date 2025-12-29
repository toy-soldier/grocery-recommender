"""Unit tests for fuzzy_filter.py"""

from apps.agent.models import models
from apps.agent.services import fuzzy_filter


def test_filter_catalog_basic_match(mocker):
    """Test that the service returns top matching candidates per grocery list line."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=2, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, full_name="Whole Milk 1L"),
            models.ProductLineItem(sku=2, full_name="Almond Milk Unsweetened"),
            models.ProductLineItem(sku=3, full_name="Brown Eggs Large"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(query="milk", product="milk"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert isinstance(result, models.PrunedCatalogList)
    assert len(result.lines) == 1

    line = result.lines[0]
    assert line.query == "milk"
    assert len(line.candidates) == 2
    assert {c.sku for c in line.candidates} == {1, 2}


def test_filter_catalog_unparsed_line(mocker):
    """Test that the service doesn't return candidates for an unparsed grocery list line."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=2, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, full_name="Whole Milk 1L"),
            models.ProductLineItem(sku=2, full_name="Almond Milk Unsweetened"),
            models.ProductLineItem(sku=3, full_name="Brown Eggs Large"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(query="0", product=None),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert isinstance(result, models.PrunedCatalogList)
    assert len(result.lines) == 1

    line = result.lines[0]
    assert line.query == "0"
    assert line.product is None
    assert len(line.candidates) == 0


def test_filter_catalog_respects_top_n_per_line(mocker):
    """
    Test that even when a grocery list line has multiple matches
    in the store catalog, only the top N candidates are returned per line.
    """
    service = fuzzy_filter.FuzzyFilterService(
        top_n=10, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, full_name="Milk"),
            models.ProductLineItem(sku=2, full_name="Oat Milk"),
            models.ProductLineItem(sku=3, full_name="Soy Milk"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(query="milk", product="milk"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert len(result.lines) == 1
    assert len(result.lines[0].candidates) == 3

    service = fuzzy_filter.FuzzyFilterService(
        top_n=1, min_score=60, logger=mocker.Mock()
    )

    result = service.filter_catalog(data)

    assert len(result.lines) == 1
    assert len(result.lines[0].candidates) == 1


def test_filter_catalog_respects_min_score(mocker):
    """Test that low-quality matches are excluded from per-line candidate lists."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=0, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, full_name="Milk"),
            models.ProductLineItem(sku=2, full_name="Eggs"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(query="butter", product="butter"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert len(result.lines) == 1
    assert len(result.lines[0].candidates) == 2

    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=60, logger=mocker.Mock()
    )

    result = service.filter_catalog(data)

    assert len(result.lines) == 1
    assert len(result.lines[0].candidates) == 0


def test_filter_catalog_empty_grocery_list(mocker):
    """Test that no lines are returned when the grocery list is empty."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, full_name="Milk"),
        ]
    )

    grocery_list = models.ParsedGroceryList(grocery_list=[])

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert result.lines == []


def test_filter_catalog_empty_catalog(mocker):
    """Test that each grocery list line has no candidates when the store catalog is empty."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(catalog=[])

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(query="milk", product="milk"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert len(result.lines) == 1
    assert result.lines[0].candidates == []
