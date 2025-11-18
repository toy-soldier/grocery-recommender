"""Unit tests for products.py"""


def test_retrieve_catalog(test_client):
    """Unit test for retrieve_catalog()"""
    response = test_client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json() == {
        "input": "ALL",
        "message": "Catalog successfully retrieved.",
    }


def test_get_product(test_client):
    """Unit test for get_product()"""
    response = test_client.get("/api/v1/products/123")
    assert response.status_code == 200
    assert response.json() == {
        "input": 123,
        "message": "Product successfully retrieved.",
    }
