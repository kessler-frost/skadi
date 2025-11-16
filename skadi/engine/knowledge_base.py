"""Knowledge base for PennyLane quantum computing documentation and code snippets.

This module provides a Knowledge-based RAG system using Agno's Knowledge class
with LanceDB as the vector store. It's optimized for quantum computing concepts,
PennyLane API documentation, and code examples.
"""

import os
from pathlib import Path
from typing import Optional

from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType

from skadi.config import settings


class PennyLaneKnowledge:
    """Knowledge base wrapper for PennyLane documentation and quantum computing concepts.

    This class provides a convenient interface to Agno's Knowledge system,
    configured specifically for quantum computing domain knowledge with:
    - Hybrid search (vector + keyword) for technical queries
    - Optimized chunking for code snippets and conceptual explanations
    - OpenAI embeddings for semantic understanding
    - LanceDB for fast vector storage and retrieval
    """

    def __init__(
        self,
        db_uri: Optional[str] = None,
        table_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        api_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """Initialize the PennyLane Knowledge base.

        Args:
            db_uri: Path to the LanceDB database directory. If None, uses settings.lancedb_uri.
            table_name: Name of the table in LanceDB. If None, uses settings.lancedb_table.
            embedding_model: OpenAI embedding model ID. If None, uses settings.embedding_model.
            api_key: OpenAI API key. If None, uses settings.openai_api_key.
            chunk_size: Size of text chunks for embedding (in characters). If None, uses settings.chunk_size.
            chunk_overlap: Number of overlapping characters between chunks. If None, uses settings.chunk_overlap.

        Raises:
            ValueError: If API key is not provided and not found in settings.
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or pass api_key to PennyLaneKnowledge constructor."
            )

        # Set the API key in environment for OpenAI embedder
        os.environ["OPENAI_API_KEY"] = self.api_key

        self.db_uri = db_uri or settings.lancedb_uri
        self.table_name = table_name or settings.lancedb_table
        self.embedding_model = embedding_model or settings.embedding_model
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        # Initialize embedder
        self.embedder = OpenAIEmbedder(
            id=self.embedding_model,
            dimensions=1536,  # text-embedding-3-small produces 1536-dim vectors
        )

        # Initialize LanceDB vector store with hybrid search
        # Hybrid search combines vector similarity with keyword matching,
        # which is ideal for technical documentation where exact terms matter
        self.vector_db = LanceDb(
            uri=self.db_uri,
            table_name=self.table_name,
            search_type=SearchType.hybrid,
            embedder=self.embedder,
        )

        # Initialize the Knowledge base
        self.knowledge = Knowledge(
            name="PennyLane Documentation",
            description=(
                "PennyLane quantum computing documentation, API references, "
                "tutorials, and code examples for quantum circuit manipulation."
            ),
            vector_db=self.vector_db,
        )

    def add_text(
        self,
        content: str,
        name: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add text content to the knowledge base.

        Args:
            content: The text content to add.
            name: Unique identifier/name for this content.
            metadata: Optional metadata dict to attach to the content.
                Useful for filtering and tracking document sources.
        """
        self.knowledge.add_content(
            name=name,
            content=content,
            metadata=metadata or {},
        )

    def add_file(
        self,
        file_path: str | Path,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add content from a file to the knowledge base.

        Supports: .txt, .md, .py, .json, .pdf, .docx

        Args:
            file_path: Path to the file to add.
            name: Optional unique identifier. If None, uses filename.
            metadata: Optional metadata dict to attach to the content.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content_name = name or file_path.name

        self.knowledge.add_content(
            name=content_name,
            path=str(file_path),
            metadata=metadata or {},
        )

    def add_url(
        self,
        url: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add content from a URL to the knowledge base.

        Args:
            url: URL to fetch content from.
            name: Optional unique identifier. If None, uses URL as name.
            metadata: Optional metadata dict to attach to the content.
        """
        content_name = name or url

        self.knowledge.add_content(
            name=content_name,
            url=url,
            metadata=metadata or {},
        )

    def search(
        self,
        query: str,
        num_results: int = 5,
    ) -> list[dict]:
        """Search the knowledge base for relevant content.

        Uses hybrid search (vector similarity + keyword matching) to find
        the most relevant content chunks for the given query.

        Args:
            query: The search query.
            num_results: Maximum number of results to return. Defaults to 5.

        Returns:
            List of dictionaries containing matched content and metadata.
            Each dict has keys: 'content', 'name', 'metadata', 'score'.
        """
        results = self.knowledge.search(query=query, num_documents=num_results)
        return results

    def clear(self) -> None:
        """Clear all content from the knowledge base.

        Warning: This will delete all documents and embeddings from the vector store.
        """
        self.knowledge.clear()


def initialize_pennylane_knowledge(
    docs_dir: Optional[str | Path] = None,
    db_uri: Optional[str] = None,
    force_reload: bool = False,
) -> PennyLaneKnowledge:
    """Initialize the PennyLane knowledge base with documentation.

    This function creates a PennyLaneKnowledge instance and loads all
    documentation files from the specified directory.

    Args:
        docs_dir: Path to directory containing PennyLane documentation.
            If None, uses settings.scraper_output_dir.
        db_uri: Path to the LanceDB database directory.
            If None, uses settings.lancedb_uri.
        force_reload: If True, clears existing knowledge and reloads everything.
            If False, only adds new documents. Defaults to False.

    Returns:
        Initialized PennyLaneKnowledge instance with loaded documentation.

    Raises:
        FileNotFoundError: If docs_dir doesn't exist.
    """
    docs_path = Path(docs_dir or settings.scraper_output_dir)
    if not docs_path.exists():
        raise FileNotFoundError(
            f"Documentation directory not found: {docs_path}. "
            "Please ensure PennyLane documentation has been scraped to this location."
        )

    # Initialize knowledge base
    kb = PennyLaneKnowledge(db_uri=db_uri)

    # Clear existing knowledge if force_reload is True
    if force_reload:
        kb.clear()

    # Supported file extensions for different document types
    supported_extensions = {".txt", ".md", ".py", ".json", ".pdf", ".docx"}

    # Load all documentation files
    loaded_count = 0
    for file_path in docs_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in supported_extensions:
            try:
                # Create relative path for better organization
                rel_path = file_path.relative_to(docs_path)

                # Add metadata about the document source
                metadata = {
                    "source": "pennylane_docs",
                    "file_type": file_path.suffix,
                    "relative_path": str(rel_path),
                }

                kb.add_file(
                    file_path=file_path,
                    name=str(rel_path),
                    metadata=metadata,
                )

                loaded_count += 1

            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")
                continue

    print(f"Loaded {loaded_count} documents into PennyLane knowledge base.")

    return kb


def get_knowledge_for_agent(
    db_uri: Optional[str] = None,
    table_name: Optional[str] = None,
) -> Knowledge:
    """Get a Knowledge instance configured for use with Agno agents.

    This is a convenience function that returns the underlying Knowledge object
    that can be directly passed to an Agent's knowledge parameter.

    Args:
        db_uri: Path to the LanceDB database directory. If None, uses settings.lancedb_uri.
        table_name: Name of the table in LanceDB. If None, uses settings.lancedb_table.

    Returns:
        Configured Knowledge instance ready for agent integration.

    Example:
        >>> from agno.agent import Agent
        >>> from agno.models.openrouter import OpenRouter
        >>> from skadi.engine.knowledge_base import get_knowledge_for_agent
        >>>
        >>> knowledge = get_knowledge_for_agent()
        >>> agent = Agent(
        ...     model=OpenRouter(id="anthropic/claude-haiku-4.5"),
        ...     knowledge=knowledge,
        ...     instructions=["Search your knowledge before answering questions."]
        ... )
    """
    kb = PennyLaneKnowledge(db_uri=db_uri, table_name=table_name)
    return kb.knowledge
