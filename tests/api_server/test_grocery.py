"""Unit tests for grocery.py"""


def test_home(test_client):
    """Unit test for home()"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the application's homepage."}


def test_health(test_client):
    """Unit test for health()"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "All is well."}
