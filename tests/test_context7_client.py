"""Tests for Context7 MCP client."""

from skadi.engine.context7_client import Context7Client


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
