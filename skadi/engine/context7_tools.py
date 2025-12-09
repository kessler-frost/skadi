"""Context7 toolkit for querying PennyLane documentation."""

import httpx
from agno.tools import Toolkit

from skadi.config import settings


class Context7Tools(Toolkit):
    """Toolkit for querying PennyLane documentation via Context7 API."""

    def __init__(self, api_key: str | None = None, **kwargs):
        """
        Initialize the Context7 toolkit.

        Args:
            api_key: Optional Context7 API key for authentication (higher rate limits).
                    If None, uses settings.context7_api_key. Works without key (lower limits).
            **kwargs: Additional arguments passed to parent Toolkit.
        """
        tools = [self.search_pennylane_docs]
        instructions = (
            "Use this tool to look up PennyLane documentation when you need to verify "
            "API usage or find correct syntax for quantum operations."
        )
        super().__init__(
            name="context7_tools", tools=tools, instructions=instructions, **kwargs
        )
        self.api_key = api_key or settings.context7_api_key

    def search_pennylane_docs(self, topic: str) -> str:
        """
        Search PennyLane documentation for a specific topic.

        Args:
            topic: The topic to search for (e.g., "CNOT gate", "qml.Hadamard", "quantum state")

        Returns:
            Documentation snippets related to the topic.
        """
        url = "https://context7.com/api/v2/docs/code/pennylaneai/pennylane"
        params = {"topic": topic}

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = httpx.get(url, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()

        data = response.json()
        snippets = data.get("snippets", [])

        if not snippets:
            return f"No documentation found for topic: {topic}"

        # Format the snippets for the LLM
        formatted_output = [f"# PennyLane Documentation for: {topic}\n"]

        for i, snippet in enumerate(snippets, 1):
            title = snippet.get("title", "Untitled")
            content = snippet.get("content", "")
            url = snippet.get("url", "")

            formatted_output.append(f"## Result {i}: {title}")
            if url:
                formatted_output.append(f"URL: {url}")
            formatted_output.append(f"\n{content}\n")
            formatted_output.append("-" * 80)

        return "\n".join(formatted_output)
