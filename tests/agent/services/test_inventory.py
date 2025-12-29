"""Unit tests for inventory.py"""

import copy

import pytest
import tenacity

from apps.agent.dependencies import exceptions as exc
from apps.agent.models import models
from apps.agent.services import inventory as inv


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param(100, (None, 100), id="Returns correct product details"),
        pytest.param(
            990, (exc.ProductNotFoundException, -1), id="Returns blank product details"
        ),
        pytest.param(
            200, (tenacity.RetryError, -1), id="Also returns blank product details"
        ),
    ],
)
def test_get_product(mocked_api_client, mocker, test_input, expected):
    """
    Unit test for get_product().
    Test the method on various inputs and check the returned value.
    """
    expected_exc_class, expected_sku = expected
    if not expected_exc_class:
        mocked_api_client.return_value.get_product_details.return_value = {
            "data": {
                "brand": "Test Brand",
                "description": "Test Description",
                "qty_in_stock": 34,
                "sku": expected_sku,
                "unit_price": 7.69,
            }
        }
    else:
        if expected_exc_class == tenacity.RetryError:
            mocked_exc = expected_exc_class(mocker.Mock())
        else:
            mocked_exc = expected_exc_class()
        mocked_api_client.return_value.get_product_details.side_effect = mocked_exc

    service = inv.InventoryService(logger=mocker.Mock())
    response = service.get_product(test_input)

    assert "data" in response

    if not expected_exc_class:
        # success case should preserve all values
        assert response["data"]["sku"] == expected_sku
        assert "brand" in response["data"]
        assert "unit_price" in response["data"]
        assert "description" in response["data"]
        assert "qty_in_stock" in response["data"]
    else:
        # failure case should contain sku=-1 only
        assert response["data"]["sku"] == -1
        assert len(response["data"]) == 1


def test_load_catalog_on_one_page(mocked_api_client, mocker):
    """Check that load_catalog() works properly on one page."""
    service = inv.InventoryService(logger=mocker.Mock())
    response = {
        "count": 1,
        "data": [{"full_name": "Test Product 35", "sku": 35}],
        "next": None,
        "previous": None,
    }
    mocked_api_client.return_value.get_product_listing.return_value = response
    service.load_catalog(100)
    assert service.catalog == models.ProductCatalog(catalog=[models.ProductLineItem(full_name="Test Product 35", sku=35)])


def test_load_catalog_on_multiple_pages(mocked_api_client, mocker):
    """Check that load_catalog() works properly on pages with results."""
    expected_catalog = []
    for i in range(12):
        product = {"full_name": f"Test Product {i}", "sku": i}
        expected_catalog.append(models.ProductLineItem(**product))
    client_responses = []
    for i in range(4):
        response = {"count": 3, "data": [], "next": "exists", "previous": "exists"}
        if i == 0:
            response["previous"] = None
        if i == 3:
            response["next"] = None
        data = []
        for j in range(3):
            product = copy.copy(expected_catalog[i * 3 + j])
            data.append(product)
        response["data"] = data
        client_responses.append(response)

    service = inv.InventoryService(logger=mocker.Mock())
    mocked_api_client.return_value.get_product_listing.side_effect = tuple(
        client_responses
    )
    service.load_catalog(100)
    assert service.catalog == models.ProductCatalog(catalog=expected_catalog)


def test_load_catalog_raises_exc_on_page_1(mocked_api_client, mocker):
    """Check that an exception when loading page 1 sets the catalog to []."""
    service = inv.InventoryService(logger=mocker.Mock())
    mocked_api_client.return_value.get_product_listing.side_effect = (
        tenacity.RetryError(mocker.Mock())
    )
    service.load_catalog(100)
    assert service.catalog == models.ProductCatalog(catalog=[])


def test_load_catalog_raises_exc_on_page_2(mocked_api_client, mocker):
    """Check that an exception when loading page 2 sets the catalog to []."""
    response = {
        "count": 1,
        "data": [{"full_name": "Test Product 9", "sku": 9}],
        "next": "exists",
        "previous": None,
    }
    service = inv.InventoryService(logger=mocker.Mock())
    mocked_api_client.return_value.get_product_listing.side_effect = (
        response,
        tenacity.RetryError(mocker.Mock()),
    )
    service.load_catalog(100)
    assert service.catalog == models.ProductCatalog(catalog=[])
