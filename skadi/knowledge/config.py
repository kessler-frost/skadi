"""Configuration for knowledge augmentation system."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class KnowledgeConfig:
    """Configuration for knowledge augmentation."""

    # Enable/disable knowledge augmentation
    use_knowledge: bool = True

    # PennyLane knowledge base settings
    use_pennylane_kb: bool = True
    pennylane_kb_top_k: int = 3

    # Context7 settings
    use_context7: bool = True
    context7_top_k: int = 5
    context7_library_id: str = "/pennylane/pennylane"

    # Prompt augmentation settings
    max_knowledge_tokens: int = 2000
    knowledge_priority: str = "balanced"  # "conceptual", "api", or "balanced"

    # Reranking settings
    use_reranking: bool = True
    reranking_method: str = "simple"  # "simple" or "cohere" (future)

    # API keys (optional, can use environment variables)
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.use_knowledge:
            return

        if not self.use_pennylane_kb and not self.use_context7:
            raise ValueError(
                "At least one knowledge source must be enabled when use_knowledge=True"
            )

        if self.knowledge_priority not in ["conceptual", "api", "balanced"]:
            raise ValueError(
                f"Invalid knowledge_priority: {self.knowledge_priority}. "
                "Must be 'conceptual', 'api', or 'balanced'"
            )

        if self.reranking_method not in ["simple", "cohere"]:
            raise ValueError(
                f"Invalid reranking_method: {self.reranking_method}. "
                "Must be 'simple' or 'cohere'"
            )


# Default configuration
DEFAULT_CONFIG = KnowledgeConfig()
