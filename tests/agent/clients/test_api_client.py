"""Unit tests for api_client.py"""

import pytest
import requests
import tenacity

from apps.agent.clients import api_client
from apps.agent.dependencies import exceptions as exc


def test_get_product_details_on_existing_product(mocker, mocked_get):
    """Test that the client returns the details of an existing product."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 200
    mocked_json_response = {
        "data": {
            "brand": "Phoenix",
            "description": "canned chickpeas - 450g",
            "qty_in_stock": 34,
            "sku": 50017,
            "unit_price": 7.69,
        }
    }
    mocked_response.json.return_value = mocked_json_response
    mocked_get.return_value = mocked_response
    response = client.get_product_details(50017)
    assert response == mocked_json_response
    assert mocked_get.call_count == 1


def test_get_product_details_on_non_existing_product(mocker, mocked_get):
    """Test that the client raises ProductNotFoundException for a non-existing product."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 404
    mocked_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_response
    )
    mocked_get.return_value = mocked_response
    with pytest.raises(exc.ProductNotFoundException):
        client.get_product_details(999)
    assert mocked_get.call_count == 1


def test_get_product_details_raises_504(mocker, mocked_get):
    """Test that the client raises APIServerException for a non-404 response."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 504
    mocked_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_response
    )
    mocked_get.return_value = mocked_response
    with pytest.raises(tenacity.RetryError):
        client.get_product_details(999)
    assert mocked_get.call_count == 3


def test_get_product_details_raises_some_other_error(mocker, mocked_get):
    """Test that the client raises APIServerException for a generic error."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_get.side_effect = Exception("Something went wrong")
    with pytest.raises(tenacity.RetryError):
        client.get_product_details(999)
    assert mocked_get.call_count == 3


def test_get_product_details_on_existing_product_succeeds_after_two_failures(
    mocker, mocked_get
):
    """Test that the client returns the details of an existing product even after two failures."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_good_response = mocker.Mock()
    mocked_good_response.status_code = 200
    mocked_json_response = {
        "data": {
            "brand": "Phoenix",
            "description": "canned chickpeas - 450g",
            "qty_in_stock": 34,
            "sku": 50017,
            "unit_price": 7.69,
        }
    }
    mocked_good_response.json.return_value = mocked_json_response

    mocked_bad_response = mocker.Mock()
    mocked_bad_response.status_code = 403
    mocked_bad_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_bad_response
    )

    mocked_get.side_effect = (
        Exception("Something went wrong"),
        mocked_bad_response,
        mocked_good_response,
    )
    response = client.get_product_details(50017)
    assert response == mocked_json_response
    assert mocked_get.call_count == 3


def test_get_product_details_on_non_existing_product_stops_immediately(
    mocker, mocked_get
):
    """Test that the client raises ProductNotFoundException for a non-existing product, even after one retry."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 404
    mocked_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_response
    )
    mocked_get.side_effect = (
        Exception("something went wrong"),
        mocked_response,
        Exception("something went wrong"),
    )
    with pytest.raises(exc.ProductNotFoundException):
        client.get_product_details(999)
    assert mocked_get.call_count == 2


def test_get_product_listing_returns_200(mocker, mocked_get):
    """Test that the client returns the product listing."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 200
    mocked_json_response = {"data": []}
    mocked_response.json.return_value = mocked_json_response
    mocked_get.return_value = mocked_response
    response = client.get_product_listing(1, 5)
    assert response == mocked_json_response
    assert mocked_get.call_count == 1


def test_get_product_listing_raises_504(mocker, mocked_get):
    """Test that the client raises APIServerException for a non-200 response."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_response = mocker.Mock()
    mocked_response.status_code = 504
    mocked_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_response
    )
    mocked_get.return_value = mocked_response
    with pytest.raises(tenacity.RetryError):
        client.get_product_listing(1, 5)
    assert mocked_get.call_count == 3


def test_get_product_listing_raises_some_other_error(mocker, mocked_get):
    """Test that the client raises APIServerException for a generic error."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_get.side_effect = Exception("Something went wrong")
    with pytest.raises(tenacity.RetryError):
        client.get_product_listing(1, 5)
    assert mocked_get.call_count == 3


def test_get_product_listing_succeeds_after_two_failures(mocker, mocked_get):
    """Test that the client returns the product listing even after two failures."""
    client = api_client.APIClient(logger=mocker.Mock())
    mocked_good_response = mocker.Mock()
    mocked_good_response.status_code = 200
    mocked_json_response = {"data": []}
    mocked_good_response.json.return_value = mocked_json_response

    mocked_bad_response = mocker.Mock()
    mocked_bad_response.status_code = 403
    mocked_bad_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocked_bad_response
    )

    mocked_get.side_effect = (
        Exception("Something went wrong"),
        mocked_bad_response,
        mocked_good_response,
    )
    response = client.get_product_listing(1, 5)
    assert response == mocked_json_response
    assert mocked_get.call_count == 3
