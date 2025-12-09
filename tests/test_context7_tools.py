"""Tests for Context7 toolkit."""

import pytest
from unittest.mock import Mock, patch

from skadi.engine.context7_tools import Context7Tools


@pytest.mark.unit
def test_context7_tools_initialization():
    """Test Context7Tools initialization."""
    toolkit = Context7Tools()
    assert toolkit.name == "context7_tools"
    assert len(toolkit.tools) == 1
    assert toolkit.tools[0].__name__ == "search_pennylane_docs"


@pytest.mark.unit
def test_context7_tools_with_api_key():
    """Test Context7Tools initialization with API key."""
    api_key = "test_api_key"
    toolkit = Context7Tools(api_key=api_key)
    assert toolkit.api_key == api_key


@pytest.mark.unit
@patch("skadi.engine.context7_tools.httpx.get")
def test_search_pennylane_docs_success(mock_get):
    """Test successful documentation search."""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "snippets": [
            {
                "title": "CNOT Gate",
                "content": "The CNOT gate is a two-qubit gate...",
                "url": "https://docs.pennylane.ai/en/stable/code/api/pennylane.CNOT.html",
            }
        ]
    }
    mock_get.return_value = mock_response

    toolkit = Context7Tools()
    result = toolkit.search_pennylane_docs("CNOT gate")

    assert "CNOT Gate" in result
    assert "The CNOT gate is a two-qubit gate" in result
    assert "https://docs.pennylane.ai" in result


@pytest.mark.unit
@patch("skadi.engine.context7_tools.httpx.get")
def test_search_pennylane_docs_no_results(mock_get):
    """Test documentation search with no results."""
    # Mock empty response
    mock_response = Mock()
    mock_response.json.return_value = {"snippets": []}
    mock_get.return_value = mock_response

    toolkit = Context7Tools()
    result = toolkit.search_pennylane_docs("nonexistent_topic")

    assert "No documentation found" in result
    assert "nonexistent_topic" in result


@pytest.mark.unit
@patch("skadi.engine.context7_tools.httpx.get")
def test_search_pennylane_docs_with_auth(mock_get):
    """Test documentation search with API key authentication."""
    mock_response = Mock()
    mock_response.json.return_value = {"snippets": []}
    mock_get.return_value = mock_response

    api_key = "test_api_key"
    toolkit = Context7Tools(api_key=api_key)
    toolkit.search_pennylane_docs("test_topic")

    # Verify the Authorization header was set
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "headers" in call_args.kwargs
    assert call_args.kwargs["headers"]["Authorization"] == f"Bearer {api_key}"


@pytest.mark.unit
@patch("skadi.engine.context7_tools.httpx.get")
def test_search_pennylane_docs_multiple_snippets(mock_get):
    """Test documentation search with multiple results."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "snippets": [
            {
                "title": "Hadamard Gate",
                "content": "The Hadamard gate creates superposition...",
                "url": "https://docs.pennylane.ai/hadamard",
            },
            {
                "title": "Hadamard Transform",
                "content": "The Hadamard transform is a generalization...",
                "url": "https://docs.pennylane.ai/hadamard-transform",
            },
        ]
    }
    mock_get.return_value = mock_response

    toolkit = Context7Tools()
    result = toolkit.search_pennylane_docs("Hadamard")

    assert "Result 1: Hadamard Gate" in result
    assert "Result 2: Hadamard Transform" in result
    assert "creates superposition" in result
    assert "generalization" in result
