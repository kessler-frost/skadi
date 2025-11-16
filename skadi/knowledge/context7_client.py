"""Context7 MCP client for fetching PennyLane API documentation.

This module provides a client that uses the real Context7 MCP tools to fetch
PennyLane documentation dynamically. It replaces the previous static knowledge base
with live documentation retrieval.

Cache Implementation Note:
    We use a simple dict-based cache instead of functools.lru_cache because:
    1. We need instance-level caching (lru_cache is function-level)
    2. We need custom cache key generation based on multiple parameters
    3. We want fine-grained cache control (clear_cache, get_cache_stats)
    4. We need to manually add items via cache_docs() method
    5. The dict maintains insertion order (Python 3.7+), enabling simple LRU-style eviction
"""

import hashlib
from typing import Optional


class Context7Client:
    """
    Client for fetching PennyLane documentation from Context7 via MCP.

    This client uses the Context7 MCP tools (resolve-library-id and get-library-docs)
    to fetch up-to-date PennyLane documentation. It includes caching to minimize
    redundant MCP calls.

    The client provides the same interface as the previous static client but fetches
    documentation dynamically from Context7.
    """

    PENNYLANE_LIBRARY_ID = "/pennylaneai/pennylane"
    DEFAULT_TOKEN_LIMIT = 2000
    MAX_CACHE_SIZE = 50

    def __init__(self, library_id: Optional[str] = None):
        """
        Initialize the Context7 client.

        Args:
            library_id: Context7-compatible library ID. If None, uses PENNYLANE_LIBRARY_ID.
        """
        self.library_id = library_id or self.PENNYLANE_LIBRARY_ID
        self.cache = {}
        self.max_cache_size = self.MAX_CACHE_SIZE

    def _cache_key(self, topic: str, tokens: int) -> str:
        """
        Generate a cache key from topic and token limit.

        Args:
            topic: Documentation topic to query.
            tokens: Token limit for the query.

        Returns:
            MD5 hash of the query parameters.
        """
        key_data = f"{self.library_id}:{topic}:{tokens}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _add_to_cache(self, key: str, value: str) -> None:
        """
        Add entry to cache with LRU-style eviction.

        Args:
            key: Cache key.
            value: Documentation content to cache.
        """
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (first item in dict)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = value

    def get_docs(
        self, topic: str, tokens: Optional[int] = None, use_cache: bool = True
    ) -> Optional[str]:
        """
        Retrieve PennyLane documentation for a specific topic via Context7 MCP.

        This method queries Context7 MCP for PennyLane documentation related to the
        specified topic. Results are cached to avoid redundant MCP calls.

        Args:
            topic: Topic or keywords to search for (e.g., "qml.Hadamard",
                   "qnode decorator", "CNOT gate").
            tokens: Maximum tokens to retrieve (default: 2000).
            use_cache: Whether to use cached results if available.

        Returns:
            Documentation string if found, None if query fails or no results.

        Note:
            This method calls the Context7 MCP tool. The actual MCP call must be made
            by the calling code since we cannot directly invoke MCP tools from within
            the class. Instead, this returns a placeholder that signals the need for
            an MCP call.

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

        # Return None to indicate MCP call is needed
        # The calling code should detect this and make the MCP call
        return None

    def cache_docs(self, topic: str, docs: str, tokens: Optional[int] = None) -> None:
        """
        Manually cache documentation retrieved from Context7 MCP.

        This method is used after making an MCP call to store the results.

        Args:
            topic: Topic that was queried.
            docs: Documentation content retrieved from MCP.
            tokens: Token limit used in the query.
        """
        if tokens is None:
            tokens = self.DEFAULT_TOKEN_LIMIT

        cache_key = self._cache_key(topic, tokens)
        self._add_to_cache(cache_key, docs)

    def get_context(self, query: str, max_docs: int = 5) -> str:
        """
        Get formatted API documentation context for circuit generation.

        This is a compatibility method that provides the same interface as the
        previous static client. It returns a formatted string of documentation
        or an empty string if the MCP call is needed.

        Args:
            query: Circuit description query.
            max_docs: Maximum number of API docs to include (not used with MCP).

        Returns:
            Formatted API documentation as a string, or empty string if MCP call needed.

        Note:
            For the MCP version, this method checks the cache. If not cached,
            it returns an empty string, signaling that the calling code should
            make an MCP call via get_docs().
        """
        # Try to get from cache
        docs = self.get_docs(query, use_cache=True)

        if docs:
            # Format the documentation
            return self._format_docs(docs)

        # Return empty string if not cached (MCP call needed)
        return ""

    def _format_docs(self, docs: str) -> str:
        """
        Format raw documentation for prompt injection.

        Args:
            docs: Raw documentation from Context7.

        Returns:
            Formatted documentation string.
        """
        if not docs:
            return ""

        # Add header
        formatted = "## Relevant PennyLane API:\n\n"
        formatted += docs

        return formatted

    def fetch_docs(
        self, topic: str, context7_library_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetch documentation from Context7 MCP.

        This is a compatibility method that was used in the previous implementation.
        It now uses the MCP-based approach.

        Args:
            topic: Topic to fetch documentation for.
            context7_library_id: Context7 library identifier (defaults to PENNYLANE_LIBRARY_ID).

        Returns:
            Documentation string from cache, or None if MCP call needed.
        """
        if context7_library_id:
            self.library_id = context7_library_id

        return self.get_docs(topic)

    def clear_cache(self) -> None:
        """Clear the documentation cache."""
        self.cache.clear()

    def get_cache_stats(self) -> dict:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache size and key information.
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_cache_size,
            "keys": list(self.cache.keys()),
        }

    def extract_code_snippets(self, docs: str) -> list[str]:
        """
        Extract code snippets from Context7 documentation response.

        Context7 returns documentation with code blocks in markdown format.
        This method extracts just the Python code snippets.

        Args:
            docs: Documentation string from Context7.

        Returns:
            List of code snippet strings.

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
        """
        Format Context7 documentation for inclusion in LLM prompts.

        Extracts and formats the most relevant code snippets for prompt injection.

        Args:
            docs: Documentation string from Context7.
            max_snippets: Maximum number of code snippets to include.

        Returns:
            Formatted string suitable for LLM prompt inclusion.
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

    # Convenience methods for common queries

    def get_operation_docs(self, operation: str) -> Optional[str]:
        """
        Get documentation for a specific PennyLane operation.

        Args:
            operation: Operation name (e.g., "Hadamard", "CNOT", "RX", "expval").

        Returns:
            Documentation string if found, None otherwise.
        """
        topic = f"qml.{operation} {operation} gate operation"
        return self.get_docs(topic)

    def get_decorator_docs(self, decorator: str) -> Optional[str]:
        """
        Get documentation for PennyLane decorators.

        Args:
            decorator: Decorator name (e.g., "qnode", "qfunc_transform").

        Returns:
            Documentation string if found, None otherwise.
        """
        topic = f"@qml.{decorator} {decorator} decorator"
        return self.get_docs(topic)

    def get_device_docs(self, device_type: str = "default.qubit") -> Optional[str]:
        """
        Get documentation for PennyLane devices.

        Args:
            device_type: Device type (e.g., "default.qubit", "default.mixed").

        Returns:
            Documentation string if found, None otherwise.
        """
        topic = f"qml.device {device_type} device initialization"
        return self.get_docs(topic)

    def get_template_docs(self, template: str) -> Optional[str]:
        """
        Get documentation for PennyLane circuit templates.

        Args:
            template: Template name (e.g., "AngleEmbedding", "StronglyEntanglingLayers").

        Returns:
            Documentation string if found, None otherwise.
        """
        topic = f"qml.{template} {template} template circuit"
        return self.get_docs(topic)

    # New MCP-specific methods

    @staticmethod
    def resolve_library_id(library_name: str) -> Optional[str]:
        """
        Resolve a library name to its Context7-compatible library ID.

        This method is a placeholder that signals the need for an MCP call.
        The actual resolution must be done by calling code using the
        mcp__context7__resolve-library-id tool.

        Args:
            library_name: Name of the library to resolve (e.g., "pennylane").

        Returns:
            None (signals that MCP call is needed).

        Note:
            The calling code should use mcp__context7__resolve-library-id
            and then create a Context7Client with the returned library_id.
        """
        return None

    def needs_mcp_call(self, topic: str, tokens: Optional[int] = None) -> bool:
        """
        Check if an MCP call is needed for a given topic.

        Args:
            topic: Topic to check.
            tokens: Token limit to check.

        Returns:
            True if MCP call is needed (not in cache), False otherwise.
        """
        if tokens is None:
            tokens = self.DEFAULT_TOKEN_LIMIT

        cache_key = self._cache_key(topic, tokens)
        return cache_key not in self.cache

    def search(self, query: str, top_k: int = 3, **kwargs) -> list[dict[str, any]]:
        """
        Search for relevant documentation (compatibility method for KnowledgeSource protocol).

        This method provides a consistent interface with other knowledge sources.
        For Context7Client, it returns a single result if documentation is cached,
        or an empty list if an MCP call is needed.

        Args:
            query: Search query.
            top_k: Maximum number of results (not used, Context7 returns one aggregated result).
            **kwargs: Additional parameters (not used).

        Returns:
            List containing a single result dict if cached, empty list otherwise.
            Result format: [{"content": str, "score": float, "source": "context7"}]
        """
        docs = self.get_docs(query, use_cache=True)

        if docs:
            return [
                {
                    "content": docs,
                    "score": 1.0,
                    "source": "context7",
                    "type": "api_documentation",
                }
            ]

        return []
