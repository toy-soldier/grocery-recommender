"""Unit tests for grocery.py"""


def test_home(test_client):
    """Unit test for home()"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the application's homepage."}
