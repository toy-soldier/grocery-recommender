"""Unit tests for agent_interface.py"""

import copy
import json
import re

from apps.web_app import agent_interface as ai

TEST_FILES_LOCATION = "tests/web_app/test_files/"
filename = "mocked_response.json"
sample_response = json.load(open(TEST_FILES_LOCATION + filename, "rb"))


def test_no_recommendations(mocked_agent):
    """Unit test for a grocery list with no recommendations."""
    response = copy.copy(sample_response)
    response["recommendations"] = []
    mocked_agent.process.return_value = response
    html = ai.send_to_agent("test", "", mocked_agent)
    assert html == ""


def test_one_product_no_suggestions(mocked_agent):
    """Unit test for a grocery list with one product but no suggestions."""
    response = copy.copy(sample_response)
    response["recommendations"] = [{"query": "product A", "suggestions": []}]
    mocked_agent.process.return_value = response
    html = ai.send_to_agent("test", "", mocked_agent)
    assert html == "<h4>For your requirement `product A`...</h4>"


def test_full_recommendations(mocked_agent):
    """Unit test for a grocery list with 2 sets of product recommendations."""
    mocked_agent.process.return_value = sample_response
    html = ai.send_to_agent("test", "", mocked_agent)
    assert len(re.findall("<h4>", html)) == 2
    assert len(re.findall("checkbox", html)) == 6
