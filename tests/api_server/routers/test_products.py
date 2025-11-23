"""Unit tests for products.py"""


def test_retrieve_listing(test_client):
    """Unit test for retrieve_listing()"""
    response = test_client.get("/api/v1/products?page=5&products_per_page=3")
    assert response.status_code == 200
    assert response.json() == {
        "count": 3,
        "data": [
            {"full_name": "Terra canned mushrooms - 400g", "sku": 50204},
            {"full_name": "Twilight pretzels - 200g", "sku": 50221},
            {"full_name": "Luminous ground beef - 500g", "sku": 50238},
        ],
        "next": "/?page=6&products_per_page=3",
        "previous": "/?page=4&products_per_page=3",
    }


def test_retrieve_listing_blank_page(test_client):
    """Unit test for retrieve_listing() resulting in blank page."""
    response = test_client.get("/api/v1/products?page=2&products_per_page=30")
    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "data": [],
        "next": None,
        "previous": "/?page=1&products_per_page=30",
    }


def test_retrieve_listing_no_arguments(test_client):
    """Unit test for retrieve_listing() resulting in blank page."""
    response = test_client.get("/api/v1/products")
    assert response.status_code == 200
    resp = response.json()
    resp["data"] = []
    assert resp == {
        "count": 17,
        "data": [],
        "next": None,
        "previous": None,
    }


def test_count_calls_to_retrieve_full_listing(test_client):
    """Count the number of calls needed to get the entire catalog."""
    calls = 0
    prefix = "/api/v1/products"
    url = "?products_per_page=7"
    while url:
        response = test_client.get(prefix + url)
        assert response.status_code == 200
        calls += 1
        resp = response.json()
        url = resp["next"]
    assert calls == 3


def test_get_existing_product(test_client):
    """Unit test for get_product() of existing product."""
    response = test_client.get("/api/v1/products/50017")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "brand": "Phoenix",
            "description": "canned chickpeas - 450g",
            "qty_in_stock": 34,
            "sku": 50017,
            "unit_price": 7.69,
        }
    }


def test_get_nonexistent_product(test_client):
    """Unit test for get_product() of nonexistent product."""
    response = test_client.get("/api/v1/products/123")
    assert response.status_code == 404
