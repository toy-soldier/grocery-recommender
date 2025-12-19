"""Unit tests for fuzzy_filter.py"""

from apps.agent.models import models
from apps.agent.services import fuzzy_filter


def test_filter_catalog_basic_match(mocker):
    """Test that the service is able to prune the store catalog."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=2, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, description="Whole Milk 1L"),
            models.ProductLineItem(sku=2, description="Almond Milk Unsweetened"),
            models.ProductLineItem(sku=3, description="Brown Eggs Large"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(product="milk"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert isinstance(result, models.PrunedCatalog)
    assert len(result.catalog) == 2
    assert {item.sku for item in result.catalog} == {1, 2}


def test_filter_catalog_deduplicates_by_sku(mocker):
    """Test that the pruned catalog contains unique products only."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=2, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, description="Banana"),
            models.ProductLineItem(sku=2, description="Apple"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(product="banana"),
            models.ParsedLineItem(product="bananas"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert len(result.catalog) == 1


def test_filter_catalog_respects_min_score(mocker):
    """Test that low-quality matches are excluded from the pruned store catalog."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=0, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, description="Milk"),
            models.ProductLineItem(sku=2, description="Eggs"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(product="butter"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)
    assert len(result.catalog) == 2

    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=60, logger=mocker.Mock()
    )
    result = service.filter_catalog(data)

    assert result.catalog == []


def test_filter_catalog_empty_grocery_list(mocker):
    """Test that the pruned store catalog is empty since the list is empty."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=5, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, description="Milk"),
        ]
    )

    grocery_list = models.ParsedGroceryList(grocery_list=[])

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert result.catalog == []


def test_filter_catalog_empty_catalog(mocker):
    """Test that the pruned store catalog is empty since the catalog is empty."""
    service = fuzzy_filter.FuzzyFilterService(
        top_n=2, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(catalog=[])

    grocery_list = models.ParsedGroceryList(
        grocery_list=[models.ParsedLineItem(product="milk")]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert result.catalog == []


def test_filter_catalog_respects_top_n(mocker):
    """
    Test that the even though a product in the grocery list
    has multiple matches in the store catalog, only the top n matches
    are added to the pruned catalog.
    """
    service = fuzzy_filter.FuzzyFilterService(
        top_n=10, min_score=60, logger=mocker.Mock()
    )

    catalog = models.ProductCatalog(
        catalog=[
            models.ProductLineItem(sku=1, description="Milk"),
            models.ProductLineItem(sku=2, description="Oat Milk"),
            models.ProductLineItem(sku=3, description="Soy Milk"),
        ]
    )

    grocery_list = models.ParsedGroceryList(
        grocery_list=[
            models.ParsedLineItem(product="milk"),
        ]
    )

    data = models.CatalogForFuzzyMatching(
        catalog=catalog,
        grocery_list=grocery_list,
    )

    result = service.filter_catalog(data)

    assert len(result.catalog) == 3

    service = fuzzy_filter.FuzzyFilterService(
        top_n=1, min_score=60, logger=mocker.Mock()
    )

    result = service.filter_catalog(data)

    assert len(result.catalog) == 1
