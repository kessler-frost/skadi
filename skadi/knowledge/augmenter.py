"""Knowledge augmenter that combines multiple knowledge sources."""

from typing import Dict, List, Optional

from skadi.config import settings
from skadi.knowledge.context7_client import Context7Client
from skadi.knowledge.pennylane_kb import PennyLaneKnowledge


class KnowledgeAugmenter:
    """
    Combines multiple knowledge sources to augment circuit generation prompts.

    Integrates:
    - PennyLaneKnowledge: Conceptual understanding of quantum algorithms and patterns
    - Context7Client: API-specific documentation and code examples

    Provides unified retrieval and reranking of relevant knowledge.
    """

    def __init__(
        self,
        use_pennylane_kb: Optional[bool] = None,
        use_context7: Optional[bool] = None,
    ):
        """
        Initialize the knowledge augmenter.

        Args:
            use_pennylane_kb: Whether to use PennyLane knowledge base. If None, uses settings.use_pennylane_kb.
            use_context7: Whether to use Context7 API documentation. If None, uses settings.use_context7.
        """
        self.use_pennylane_kb = (
            use_pennylane_kb
            if use_pennylane_kb is not None
            else settings.use_pennylane_kb
        )
        self.use_context7 = (
            use_context7 if use_context7 is not None else settings.use_context7
        )

        # Initialize knowledge sources
        self.pennylane_kb = PennyLaneKnowledge() if self.use_pennylane_kb else None
        self.context7_client = Context7Client() if self.use_context7 else None

    def augment_prompt(
        self,
        user_query: str,
        base_prompt: str,
        max_knowledge_tokens: int = 2000,
    ) -> str:
        """
        Augment a base prompt with relevant knowledge from all sources.

        Args:
            user_query: User's circuit description.
            base_prompt: Base prompt template.
            max_knowledge_tokens: Maximum tokens for knowledge context (approximate).

        Returns:
            Enhanced prompt with knowledge context.
        """
        knowledge_contexts = []

        # Retrieve from PennyLane knowledge base
        if self.pennylane_kb:
            kb_context = self.pennylane_kb.get_context(user_query)
            if kb_context:
                knowledge_contexts.append(
                    {"source": "pennylane_kb", "content": kb_context, "priority": 1}
                )

        # Retrieve from Context7 API docs
        if self.context7_client:
            api_context = self.context7_client.get_context(user_query, max_docs=5)
            if api_context:
                knowledge_contexts.append(
                    {"source": "context7", "content": api_context, "priority": 2}
                )

        # Combine contexts with reranking
        combined_context = self._combine_contexts(
            knowledge_contexts, max_tokens=max_knowledge_tokens
        )

        # Insert knowledge into prompt
        if combined_context:
            enhanced_prompt = self._insert_knowledge(
                base_prompt, user_query, combined_context
            )
            return enhanced_prompt
        else:
            return base_prompt.format(description=user_query)

    def _combine_contexts(self, contexts: List[Dict], max_tokens: int = 2000) -> str:
        """
        Combine and optionally rerank knowledge contexts.

        Args:
            contexts: List of knowledge context dictionaries.
            max_tokens: Maximum tokens to include (approximate).

        Returns:
            Combined knowledge context string.
        """
        if not contexts:
            return ""

        # Sort by priority (lower number = higher priority)
        contexts.sort(key=lambda x: x["priority"])

        combined_parts = []
        estimated_tokens = 0

        for ctx in contexts:
            content = ctx["content"]
            # Rough estimate: 1 token ≈ 4 characters
            content_tokens = len(content) // 4

            if estimated_tokens + content_tokens > max_tokens:
                # Truncate if needed
                remaining_tokens = max_tokens - estimated_tokens
                if remaining_tokens > 100:  # Only add if meaningful space remains
                    truncated_content = content[: remaining_tokens * 4]
                    combined_parts.append(truncated_content)
                break

            combined_parts.append(content)
            estimated_tokens += content_tokens

        return "\n\n".join(combined_parts)

    def _insert_knowledge(
        self, base_prompt: str, user_query: str, knowledge_context: str
    ) -> str:
        """
        Insert knowledge context into the base prompt.

        Args:
            base_prompt: Base prompt template.
            user_query: User's query.
            knowledge_context: Retrieved knowledge context.

        Returns:
            Enhanced prompt with knowledge inserted.
        """
        # Create knowledge-enhanced prompt
        enhanced_prompt = f"""{base_prompt}

---

**KNOWLEDGE CONTEXT:**
The following information may help you generate the circuit:

{knowledge_context}

---

Now generate the code for: {user_query}"""

        return enhanced_prompt

    def get_retrieval_stats(self, query: str) -> Dict[str, any]:
        """
        Get statistics about knowledge retrieval for a query.

        Args:
            query: Circuit description query.

        Returns:
            Dictionary with retrieval statistics.
        """
        stats = {
            "query": query,
            "sources_enabled": [],
            "pennylane_kb_results": 0,
            "context7_results": 0,
        }

        if self.pennylane_kb:
            stats["sources_enabled"].append("pennylane_kb")
            kb_results = self.pennylane_kb.search(query, top_k=3)
            stats["pennylane_kb_results"] = len(kb_results)

        if self.context7_client:
            stats["sources_enabled"].append("context7")
            api_results = self.context7_client.get_api_docs(query, top_k=5)
            stats["context7_results"] = len(api_results)

        return stats

    def rerank_simple(
        self, query: str, contexts: List[Dict], top_k: int = 5
    ) -> List[Dict]:
        """
        Simple reranking based on keyword overlap and source priority.

        Args:
            query: Search query.
            contexts: List of context dictionaries with 'content' and 'score'.
            top_k: Number of top results to return.

        Returns:
            Reranked list of contexts.

        Note:
            This is a simple keyword-based reranker. For production,
            consider using a proper reranking model (e.g., Cohere Rerank).
        """
        query_words = set(query.lower().split())

        for ctx in contexts:
            # Calculate keyword overlap
            content_words = set(ctx["content"].lower().split())
            overlap = len(query_words & content_words)

            # Adjust score based on overlap
            ctx["adjusted_score"] = ctx.get("score", 1.0) + (overlap * 0.1)

        # Sort by adjusted score
        contexts.sort(key=lambda x: x.get("adjusted_score", 0), reverse=True)

        return contexts[:top_k]
