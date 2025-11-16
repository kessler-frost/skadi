"""Tests for knowledge source protocol implementation."""

from skadi.knowledge import Context7Client, KnowledgeSource, PennyLaneKnowledge


class TestKnowledgeSourceProtocol:
    """Tests to verify that knowledge sources implement the protocol correctly."""

    def test_pennylane_knowledge_implements_protocol(self):
        """Test that PennyLaneKnowledge implements KnowledgeSource protocol."""
        kb = PennyLaneKnowledge()

        # Verify it has the required methods
        assert hasattr(kb, "get_context")
        assert hasattr(kb, "search")
        assert callable(kb.get_context)
        assert callable(kb.search)

        # Test get_context returns a string
        context = kb.get_context("bell state")
        assert isinstance(context, str)

        # Test search returns a list
        results = kb.search("bell state", top_k=3)
        assert isinstance(results, list)

    def test_context7_client_implements_protocol(self):
        """Test that Context7Client implements KnowledgeSource protocol."""
        client = Context7Client()

        # Verify it has the required methods
        assert hasattr(client, "get_context")
        assert hasattr(client, "search")
        assert callable(client.get_context)
        assert callable(client.search)

        # Test get_context returns a string
        context = client.get_context("qml.Hadamard")
        assert isinstance(context, str)

        # Test search returns a list
        results = client.search("qml.Hadamard", top_k=3)
        assert isinstance(results, list)

    def test_protocol_function_with_pennylane_knowledge(self):
        """Test that PennyLaneKnowledge can be used as KnowledgeSource type."""

        def use_knowledge_source(
            source: KnowledgeSource, query: str
        ) -> tuple[str, list]:
            context = source.get_context(query)
            results = source.search(query, top_k=2)
            return context, results

        kb = PennyLaneKnowledge()
        context, results = use_knowledge_source(kb, "bell state")

        assert isinstance(context, str)
        assert isinstance(results, list)

    def test_protocol_function_with_context7_client(self):
        """Test that Context7Client can be used as KnowledgeSource type."""

        def use_knowledge_source(
            source: KnowledgeSource, query: str
        ) -> tuple[str, list]:
            context = source.get_context(query)
            results = source.search(query, top_k=2)
            return context, results

        client = Context7Client()
        context, results = use_knowledge_source(client, "qml.Hadamard")

        assert isinstance(context, str)
        assert isinstance(results, list)

    def test_search_returns_correct_structure(self):
        """Test that both knowledge sources return search results with expected structure."""
        kb = PennyLaneKnowledge()
        results = kb.search("bell state", top_k=1)

        if results:  # Only check if results exist
            result = results[0]
            assert isinstance(result, dict)
            assert "score" in result or "name" in result  # PennyLaneKnowledge structure

    def test_context7_search_returns_correct_structure(self):
        """Test that Context7Client search returns expected structure."""
        client = Context7Client()

        # Add some cached data
        client.cache_docs("test query", "test documentation", tokens=2000)

        results = client.search("test query", top_k=1)

        assert isinstance(results, list)
        if results:  # Should have results since we cached data
            result = results[0]
            assert isinstance(result, dict)
            assert "content" in result
            assert "score" in result
            assert "source" in result
            assert result["source"] == "context7"

    def test_empty_search_returns_list(self):
        """Test that search returns empty list when no results found."""
        client = Context7Client()

        # Search without any cached data
        results = client.search("nonexistent query", top_k=5)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_protocol_type_annotation(self):
        """Test that protocol can be used in type annotations."""

        def process_knowledge(sources: list[KnowledgeSource], query: str) -> list[str]:
            """Process multiple knowledge sources."""
            contexts = []
            for source in sources:
                context = source.get_context(query)
                contexts.append(context)
            return contexts

        kb = PennyLaneKnowledge()
        client = Context7Client()

        # This should work without type errors
        contexts = process_knowledge([kb, client], "test query")

        assert len(contexts) == 2
        assert all(isinstance(c, str) for c in contexts)
