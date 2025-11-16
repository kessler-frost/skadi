"""Tests for Context7 MCP client."""

from skadi.knowledge.context7_client import Context7Client


class TestContext7Client:
    """Test suite for Context7Client."""

    def test_initialization(self):
        """Test client initialization."""
        client = Context7Client()
        assert client.library_id == "/pennylaneai/pennylane"
        assert len(client.cache) == 0
        assert client.max_cache_size == 50

    def test_cache_key_generation(self):
        """Test cache key generation is consistent."""
        client = Context7Client()

        key1 = client._cache_key("qml.Hadamard", 3000)
        key2 = client._cache_key("qml.Hadamard", 3000)
        key3 = client._cache_key("qml.Hadamard", 2000)

        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different token limit = different key

    def test_cache_operations(self):
        """Test cache storage and retrieval."""
        client = Context7Client()

        key = client._cache_key("test", 1000)
        test_data = "Sample documentation"

        client._add_to_cache(key, test_data)
        assert key in client.cache
        assert client.cache[key] == test_data

    def test_cache_eviction(self):
        """Test LRU-style cache eviction."""
        client = Context7Client()
        client.max_cache_size = 3

        # Add 4 items to trigger eviction
        for i in range(4):
            key = client._cache_key(f"topic_{i}", 1000)
            client._add_to_cache(key, f"data_{i}")

        # Cache should only have 3 items
        assert len(client.cache) == 3

        # First item should be evicted
        first_key = client._cache_key("topic_0", 1000)
        assert first_key not in client.cache

    def test_clear_cache(self):
        """Test cache clearing."""
        client = Context7Client()

        # Add some items
        for i in range(3):
            key = client._cache_key(f"topic_{i}", 1000)
            client._add_to_cache(key, f"data_{i}")

        assert len(client.cache) == 3

        client.clear_cache()
        assert len(client.cache) == 0

    def test_get_cache_stats(self):
        """Test cache statistics retrieval."""
        client = Context7Client()

        stats = client.get_cache_stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 50

        # Add an item
        key = client._cache_key("test", 1000)
        client._add_to_cache(key, "data")

        stats = client.get_cache_stats()
        assert stats["size"] == 1
        assert key in stats["keys"]

    def test_extract_code_snippets(self):
        """Test code snippet extraction from documentation."""
        client = Context7Client()

        # Sample documentation with code blocks
        docs = """
Some text here.

```python
import pennylane as qml

dev = qml.device('default.qubit', wires=2)
```

More text.

```python
@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    return qml.state()
```
"""

        snippets = client.extract_code_snippets(docs)
        assert len(snippets) == 2
        assert "import pennylane as qml" in snippets[0]
        assert "@qml.qnode(dev)" in snippets[1]
        assert "qml.Hadamard(wires=0)" in snippets[1]

    def test_extract_code_snippets_pycon(self):
        """Test extraction of pycon-style code blocks."""
        client = Context7Client()

        docs = """
Example usage:

```pycon
>>> import pennylane as qml
>>> dev = qml.device('default.qubit', wires=1)
```
"""

        snippets = client.extract_code_snippets(docs)
        assert len(snippets) == 1
        assert ">>> import pennylane as qml" in snippets[0]

    def test_extract_code_snippets_empty(self):
        """Test extraction with no code blocks."""
        client = Context7Client()

        docs = "Just plain text with no code blocks."
        snippets = client.extract_code_snippets(docs)
        assert len(snippets) == 0

    def test_extract_code_snippets_none(self):
        """Test extraction with None input."""
        client = Context7Client()

        snippets = client.extract_code_snippets(None)
        assert len(snippets) == 0

    def test_format_for_prompt(self):
        """Test formatting documentation for prompt injection."""
        client = Context7Client()

        docs = """
```python
import pennylane as qml
```

```python
dev = qml.device('default.qubit', wires=2)
```
"""

        formatted = client.format_for_prompt(docs, max_snippets=2)
        assert "PennyLane API Reference Examples:" in formatted
        assert "Example 1:" in formatted
        assert "Example 2:" in formatted
        assert "import pennylane as qml" in formatted

    def test_format_for_prompt_limit(self):
        """Test snippet limiting in prompt formatting."""
        client = Context7Client()

        docs = """
```python
snippet1
```

```python
snippet2
```

```python
snippet3
```
"""

        formatted = client.format_for_prompt(docs, max_snippets=2)
        assert "Example 1:" in formatted
        assert "Example 2:" in formatted
        assert "Example 3:" not in formatted
        assert "snippet3" not in formatted

    def test_format_for_prompt_no_snippets(self):
        """Test prompt formatting with plain text."""
        client = Context7Client()

        docs = "Plain text documentation without code blocks. " * 50
        formatted = client.format_for_prompt(docs)

        # Should truncate to 500 chars
        assert len(formatted) <= 500
        assert formatted in docs

    def test_format_for_prompt_empty(self):
        """Test prompt formatting with empty input."""
        client = Context7Client()

        formatted = client.format_for_prompt(None)
        assert formatted == ""

        formatted = client.format_for_prompt("")
        assert formatted == ""

    def test_operation_docs_topic_formatting(self):
        """Test operation documentation query formatting."""
        client = Context7Client()

        # Mock the get_docs method to capture the topic
        called_topics = []

        def mock_get_docs(topic, tokens=None, use_cache=True):
            called_topics.append(topic)
            return None

        client.get_docs = mock_get_docs

        client.get_operation_docs("Hadamard")
        assert len(called_topics) == 1
        assert "qml.Hadamard" in called_topics[0]
        assert "Hadamard" in called_topics[0]
        assert "gate" in called_topics[0]

    def test_decorator_docs_topic_formatting(self):
        """Test decorator documentation query formatting."""
        client = Context7Client()

        called_topics = []

        def mock_get_docs(topic, tokens=None, use_cache=True):
            called_topics.append(topic)
            return None

        client.get_docs = mock_get_docs

        client.get_decorator_docs("qnode")
        assert len(called_topics) == 1
        assert "@qml.qnode" in called_topics[0]
        assert "decorator" in called_topics[0]

    def test_device_docs_topic_formatting(self):
        """Test device documentation query formatting."""
        client = Context7Client()

        called_topics = []

        def mock_get_docs(topic, tokens=None, use_cache=True):
            called_topics.append(topic)
            return None

        client.get_docs = mock_get_docs

        client.get_device_docs("default.qubit")
        assert len(called_topics) == 1
        assert "qml.device" in called_topics[0]
        assert "default.qubit" in called_topics[0]

    def test_template_docs_topic_formatting(self):
        """Test template documentation query formatting."""
        client = Context7Client()

        called_topics = []

        def mock_get_docs(topic, tokens=None, use_cache=True):
            called_topics.append(topic)
            return None

        client.get_docs = mock_get_docs

        client.get_template_docs("AngleEmbedding")
        assert len(called_topics) == 1
        assert "qml.AngleEmbedding" in called_topics[0]
        assert "template" in called_topics[0]

    def test_cache_docs_method(self):
        """Test manually caching documentation."""
        client = Context7Client()

        topic = "qml.Hadamard"
        docs = "Hadamard gate documentation"
        tokens = 2000

        # Cache the docs
        client.cache_docs(topic, docs, tokens=tokens)

        # Verify it's cached
        assert not client.needs_mcp_call(topic, tokens)

        # Retrieve from cache
        cached_docs = client.get_docs(topic, tokens=tokens)
        assert cached_docs == docs

    def test_needs_mcp_call(self):
        """Test checking if MCP call is needed."""
        client = Context7Client()

        topic = "qml.CNOT"
        tokens = 2000

        # Should need MCP call when not cached
        assert client.needs_mcp_call(topic, tokens)

        # Cache some docs
        client.cache_docs(topic, "CNOT documentation", tokens=tokens)

        # Should not need MCP call when cached
        assert not client.needs_mcp_call(topic, tokens)

        # Should need MCP call for different token count
        assert client.needs_mcp_call(topic, tokens=3000)

    def test_get_docs_returns_none_when_not_cached(self):
        """Test that get_docs returns None when not cached (signals MCP call needed)."""
        client = Context7Client()

        topic = "qml.RX"
        docs = client.get_docs(topic)

        # Should return None when not cached
        assert docs is None

    def test_get_docs_returns_cached_data(self):
        """Test that get_docs returns cached data when available."""
        client = Context7Client()

        topic = "qml.RY"
        test_docs = "RY gate rotates around Y-axis"

        # Cache the docs
        client.cache_docs(topic, test_docs)

        # Should return cached docs
        docs = client.get_docs(topic)
        assert docs == test_docs

    def test_get_context_with_cached_data(self):
        """Test get_context with cached documentation."""
        client = Context7Client()

        topic = "qml.Hadamard gates"
        test_docs = "Hadamard gate documentation content"

        # Cache the docs
        client.cache_docs(topic, test_docs)

        # Get context should format the docs
        context = client.get_context(topic)

        assert context != ""
        assert "## Relevant PennyLane API:" in context
        assert test_docs in context

    def test_get_context_without_cached_data(self):
        """Test get_context returns empty string when not cached."""
        client = Context7Client()

        topic = "qml.CNOT gates"

        # Get context should return empty string when not cached
        context = client.get_context(topic)

        assert context == ""

    def test_custom_library_id(self):
        """Test initialization with custom library ID."""
        custom_id = "/custom/library"
        client = Context7Client(library_id=custom_id)

        assert client.library_id == custom_id

    def test_fetch_docs_compatibility(self):
        """Test fetch_docs method for backward compatibility."""
        client = Context7Client()

        topic = "qml.device"
        test_docs = "Device documentation"

        # Cache docs first
        client.cache_docs(topic, test_docs)

        # fetch_docs should return cached docs
        docs = client.fetch_docs(topic)
        assert docs == test_docs

    def test_resolve_library_id_static_method(self):
        """Test resolve_library_id static method."""
        # This is a placeholder method that returns None
        result = Context7Client.resolve_library_id("pennylane")
        assert result is None  # Signals that MCP call is needed
