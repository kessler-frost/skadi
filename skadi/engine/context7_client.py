"""Context7 MCP client for PennyLane API documentation retrieval.

This module provides a client for querying PennyLane documentation via Context7 MCP.
It serves as a SECONDARY knowledge source alongside the main knowledge base, focusing
on API-specific queries like function signatures, parameters, and usage examples.
"""

import hashlib
from typing import Optional


class Context7Client:
    """Client for querying PennyLane documentation via Context7 MCP.

    This client provides access to PennyLane API documentation through Context7 MCP,
    with built-in caching to minimize redundant MCP calls. It's designed to complement
    (not replace) the main knowledge base.

    Attributes:
        library_id: Context7-compatible library ID for PennyLane
        cache: In-memory cache for documentation responses
        max_cache_size: Maximum number of cached entries
    """

    PENNYLANE_LIBRARY_ID = "/pennylaneai/pennylane"
    DEFAULT_TOKEN_LIMIT = 3000
    MAX_CACHE_SIZE = 50

    def __init__(self):
        """Initialize the Context7 client with empty cache."""
        self.library_id = self.PENNYLANE_LIBRARY_ID
        self.cache = {}
        self.max_cache_size = self.MAX_CACHE_SIZE

    def _cache_key(self, topic: str, tokens: int) -> str:
        """Generate a cache key from topic and token limit.

        Args:
            topic: Documentation topic to query
            tokens: Token limit for the query

        Returns:
            MD5 hash of the query parameters
        """
        key_data = f"{topic}:{tokens}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _add_to_cache(self, key: str, value: str) -> None:
        """Add entry to cache with LRU-style eviction.

        Args:
            key: Cache key
            value: Documentation content to cache
        """
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (first item in dict)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = value

    def get_docs(
        self, topic: str, tokens: Optional[int] = None, use_cache: bool = True
    ) -> Optional[str]:
        """Retrieve PennyLane documentation for a specific topic.

        This method queries Context7 MCP for PennyLane documentation related to the
        specified topic. Results are cached to avoid redundant MCP calls.

        Args:
            topic: Topic or keywords to search for (e.g., "qml.Hadamard",
                   "qnode decorator", "CNOT gate")
            tokens: Maximum tokens to retrieve (default: 3000)
            use_cache: Whether to use cached results if available

        Returns:
            Documentation string if found, None if query fails or no results

        Examples:
            >>> client = Context7Client()
            >>> docs = client.get_docs("qml.Hadamard qml.CNOT")
            >>> docs = client.get_docs("qnode decorator device", tokens=2000)
        """
        if tokens is None:
            tokens = self.DEFAULT_TOKEN_LIMIT

        # Check cache first
        cache_key = self._cache_key(topic, tokens)
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Note: This is a placeholder for MCP call
            # In actual implementation, this would use the MCP tools
            # For now, we'll return None to indicate MCP call needed
            # The actual MCP call will be made by the calling code
            return None
        except Exception as e:
            print(f"Context7 query failed: {e}")
            return None

    def get_operation_docs(self, operation: str) -> Optional[str]:
        """Get documentation for a specific PennyLane operation.

        Convenience method for querying documentation about quantum operations
        like gates, measurements, or observables.

        Args:
            operation: Operation name (e.g., "Hadamard", "CNOT", "RX", "expval")

        Returns:
            Documentation string if found, None otherwise

        Examples:
            >>> client = Context7Client()
            >>> hadamard_docs = client.get_operation_docs("Hadamard")
            >>> cnot_docs = client.get_operation_docs("CNOT")
        """
        # Construct topic with common variations
        topic = f"qml.{operation} {operation} gate operation"
        return self.get_docs(topic)

    def get_decorator_docs(self, decorator: str) -> Optional[str]:
        """Get documentation for PennyLane decorators.

        Convenience method for querying decorator usage patterns.

        Args:
            decorator: Decorator name (e.g., "qnode", "qfunc_transform")

        Returns:
            Documentation string if found, None otherwise

        Examples:
            >>> client = Context7Client()
            >>> qnode_docs = client.get_decorator_docs("qnode")
        """
        topic = f"@qml.{decorator} {decorator} decorator"
        return self.get_docs(topic)

    def get_device_docs(self, device_type: str = "default.qubit") -> Optional[str]:
        """Get documentation for PennyLane devices.

        Args:
            device_type: Device type (e.g., "default.qubit", "default.mixed")

        Returns:
            Documentation string if found, None otherwise

        Examples:
            >>> client = Context7Client()
            >>> device_docs = client.get_device_docs("default.qubit")
        """
        topic = f"qml.device {device_type} device initialization"
        return self.get_docs(topic)

    def get_template_docs(self, template: str) -> Optional[str]:
        """Get documentation for PennyLane circuit templates.

        Args:
            template: Template name (e.g., "AngleEmbedding", "StronglyEntanglingLayers")

        Returns:
            Documentation string if found, None otherwise

        Examples:
            >>> client = Context7Client()
            >>> template_docs = client.get_template_docs("AngleEmbedding")
        """
        topic = f"qml.{template} {template} template circuit"
        return self.get_docs(topic)

    def clear_cache(self) -> None:
        """Clear the documentation cache."""
        self.cache.clear()

    def get_cache_stats(self) -> dict:
        """Get statistics about the cache.

        Returns:
            Dictionary with cache size and key information
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_cache_size,
            "keys": list(self.cache.keys()),
        }

    def extract_code_snippets(self, docs: str) -> list[str]:
        """Extract code snippets from Context7 documentation response.

        Context7 returns documentation with code blocks in markdown format.
        This method extracts just the Python code snippets.

        Args:
            docs: Documentation string from Context7

        Returns:
            List of code snippet strings

        Examples:
            >>> client = Context7Client()
            >>> docs = client.get_docs("qml.Hadamard")
            >>> snippets = client.extract_code_snippets(docs)
        """
        if not docs:
            return []

        snippets = []
        lines = docs.split("\n")
        in_code_block = False
        current_snippet = []

        for line in lines:
            if line.strip().startswith("```python") or line.strip().startswith(
                "```pycon"
            ):
                in_code_block = True
                current_snippet = []
            elif line.strip() == "```" and in_code_block:
                in_code_block = False
                if current_snippet:
                    snippets.append("\n".join(current_snippet))
            elif in_code_block:
                current_snippet.append(line)

        return snippets

    def format_for_prompt(self, docs: str, max_snippets: int = 3) -> str:
        """Format Context7 documentation for inclusion in LLM prompts.

        Extracts and formats the most relevant code snippets for prompt injection.

        Args:
            docs: Documentation string from Context7
            max_snippets: Maximum number of code snippets to include

        Returns:
            Formatted string suitable for LLM prompt inclusion
        """
        if not docs:
            return ""

        snippets = self.extract_code_snippets(docs)

        if not snippets:
            return docs[:500]  # Return truncated text if no snippets

        formatted = "PennyLane API Reference Examples:\n\n"
        for i, snippet in enumerate(snippets[:max_snippets], 1):
            formatted += f"Example {i}:\n```python\n{snippet}\n```\n\n"

        return formatted
