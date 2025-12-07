"""Unit tests for file_uploader.py"""

TEST_FILES_LOCATION = "tests/web_app/test_files/"


def test_home(test_client, mocker):
    """Unit test for home()"""
    mocker.patch("apps.web_app.file_uploader.orchestrator.init_agent")
    response = test_client.get("/")
    assert response.status_code == 200


def test_directly_recommend(test_client):
    """Unit test for directly accessing the recommender"""
    response = test_client.get("/recommender")
    assert response.status_code == 405


def test_upload_nothing(test_client):
    """Unit test for not uploading any file."""
    data = {"file": (None, "")}
    response = test_client.post("/recommender", data=data)
    assert response.status_code == 400


def test_csv_file(test_client):
    """Unit test of uploading a csv file."""
    filename = "invalid_file.csv"
    data = {"file": (open(TEST_FILES_LOCATION + filename, "rb"), filename)}
    response = test_client.post("/recommender", data=data)
    assert response.status_code == 400


def test_empty_file(test_client):
    """Unit test of uploading an empty file."""
    filename = "empty_file.txt"
    data = {"file": (open(TEST_FILES_LOCATION + filename, "rb"), filename)}
    response = test_client.post("/recommender", data=data)
    assert response.status_code == 400


def test_file_with_spaces_and_newlines_only(test_client):
    """Unit test of uploading a file with spaces and newlines only."""
    filename = "file_with_spaces_and_newlines_only.txt"
    data = {"file": (open(TEST_FILES_LOCATION + filename, "rb"), filename)}
    response = test_client.post("/recommender", data=data)
    assert response.status_code == 400


def test_proper_file(test_client, mocker):
    """Unit test of uploading a proper file."""
    filename = "list.txt"
    data = {"file": (open(TEST_FILES_LOCATION + filename, "rb"), filename)}
    mocked_send_to_agent = mocker.patch("apps.web_app.agent_interface.send_to_agent")
    mocked_send_to_agent.return_value = ""

    response = test_client.post("/recommender", data=data)
    assert response.status_code == 200
