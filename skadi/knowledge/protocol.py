"""Protocol defining the interface for knowledge sources.

This module defines a Protocol that all knowledge sources should implement
to ensure consistent behavior across different knowledge backends.
"""

from typing import Dict, List, Protocol


class KnowledgeSource(Protocol):
    """
    Protocol defining the interface for knowledge sources.

    All knowledge sources (PennyLaneKnowledge, Context7Client, etc.) should
    implement these methods to ensure consistent behavior and interoperability.
    """

    def get_context(self, query: str) -> str:
        """
        Get formatted context string for circuit generation.

        Args:
            query: Circuit description query.

        Returns:
            Formatted knowledge context as a string. Empty string if no context found.
        """
        ...

    def search(self, query: str, top_k: int = 3, **kwargs) -> List[Dict[str, any]]:
        """
        Search the knowledge source for relevant content.

        Args:
            query: Natural language query.
            top_k: Number of top results to return.
            **kwargs: Additional search parameters specific to the implementation.

        Returns:
            List of relevant knowledge entries with scores and metadata.
        """
        ...
