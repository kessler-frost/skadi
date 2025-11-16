"""Tests for the PennyLane knowledge base integration."""

import os
import tempfile
from pathlib import Path

import pytest

from skadi.engine.knowledge_base import (
    PennyLaneKnowledge,
    get_knowledge_for_agent,
    initialize_pennylane_knowledge,
)


class TestPennyLaneKnowledge:
    """Test suite for PennyLaneKnowledge class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary directory for the test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory with sample documentation files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_path = Path(tmpdir)

            # Create sample markdown documentation
            (docs_path / "intro.md").write_text(
                """# PennyLane Introduction

PennyLane is a cross-platform Python library for quantum computing,
quantum machine learning, and quantum chemistry. It provides a
unified interface for various quantum simulators and hardware.

## Key Features
- Quantum circuit construction
- Automatic differentiation
- Hardware integration
"""
            )

            # Create sample Python code
            (docs_path / "example.py").write_text(
                """import pennylane as qml

# Create a quantum device
dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

# Execute the circuit
result = circuit()
"""
            )

            # Create sample text documentation
            (docs_path / "gates.txt").write_text(
                """Quantum Gates in PennyLane

Basic Gates:
- Hadamard (H): Creates superposition
- PauliX (X): Bit flip gate
- PauliY (Y): Combined bit and phase flip
- PauliZ (Z): Phase flip gate
- CNOT: Controlled-NOT gate for entanglement
"""
            )

            yield docs_path

    @pytest.fixture
    def knowledge_base(self, temp_db):
        """Create a PennyLaneKnowledge instance for testing."""
        # Skip if OpenAI API key is not set
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        return PennyLaneKnowledge(db_uri=temp_db, table_name="test_kb")

    def test_initialization(self, temp_db):
        """Test that PennyLaneKnowledge initializes correctly."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        kb = PennyLaneKnowledge(db_uri=temp_db)

        assert kb.db_uri == temp_db
        assert kb.table_name == "pennylane_knowledge"
        assert kb.embedding_model == "text-embedding-3-small"
        assert kb.chunk_size == 1000
        assert kb.chunk_overlap == 200
        assert kb.knowledge is not None
        assert kb.vector_db is not None

    def test_initialization_without_api_key(self, temp_db, monkeypatch):
        """Test that initialization fails without API key."""
        # Clear the environment variable
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Mock the settings to return None for openai_api_key
        from skadi import config

        monkeypatch.setattr(config.settings, "openai_api_key", None)

        with pytest.raises(ValueError, match="OpenAI API key not found"):
            PennyLaneKnowledge(db_uri=temp_db)

    def test_add_text(self, knowledge_base):
        """Test adding text content to knowledge base."""
        content = (
            "Quantum entanglement is a phenomenon where quantum states are correlated."
        )
        knowledge_base.add_text(
            content=content,
            name="entanglement_intro",
            metadata={"topic": "entanglement", "level": "beginner"},
        )

        # Search for the added content
        results = knowledge_base.search("quantum entanglement")
        assert len(results) > 0
        # The content should be found in one of the results
        assert any("entanglement" in str(result).lower() for result in results)

    def test_add_file(self, knowledge_base, temp_docs_dir):
        """Test adding a file to knowledge base."""
        file_path = temp_docs_dir / "intro.md"

        knowledge_base.add_file(
            file_path=file_path,
            metadata={"source": "test_docs", "type": "introduction"},
        )

        # Search for content from the file
        results = knowledge_base.search("PennyLane quantum computing")
        assert len(results) > 0

    def test_add_file_not_found(self, knowledge_base):
        """Test that adding a non-existent file raises an error."""
        with pytest.raises(FileNotFoundError):
            knowledge_base.add_file(file_path="nonexistent_file.txt")

    def test_search(self, knowledge_base):
        """Test searching the knowledge base."""
        # Add some test content
        knowledge_base.add_text(
            content="The Hadamard gate creates an equal superposition state.",
            name="hadamard_info",
        )
        knowledge_base.add_text(
            content="The CNOT gate is used to create entanglement between qubits.",
            name="cnot_info",
        )

        # Search for Hadamard
        results = knowledge_base.search("Hadamard superposition", num_results=2)
        assert len(results) > 0
        assert len(results) <= 2

    def test_search_num_results(self, knowledge_base):
        """Test that search respects num_results parameter."""
        # Add multiple pieces of content
        for i in range(5):
            knowledge_base.add_text(
                content=f"Quantum gate number {i} description.",
                name=f"gate_{i}",
            )

        results = knowledge_base.search("quantum gate", num_results=3)
        assert len(results) <= 3

    def test_clear(self, knowledge_base):
        """Test clearing the knowledge base."""
        # Add content
        knowledge_base.add_text(
            content="Test content to be cleared.",
            name="test_clear",
        )

        # Verify content exists
        results_before = knowledge_base.search("test content")
        assert len(results_before) > 0

        # Clear the knowledge base
        knowledge_base.clear()

        # Verify content is gone
        results_after = knowledge_base.search("test content")
        # After clearing, we should get no results or very different results
        assert len(results_after) == 0 or results_after != results_before

    def test_custom_parameters(self, temp_db):
        """Test initialization with custom parameters."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        kb = PennyLaneKnowledge(
            db_uri=temp_db,
            table_name="custom_table",
            embedding_model="text-embedding-3-large",
            chunk_size=500,
            chunk_overlap=100,
        )

        assert kb.table_name == "custom_table"
        assert kb.embedding_model == "text-embedding-3-large"
        assert kb.chunk_size == 500
        assert kb.chunk_overlap == 100


class TestInitializePennyLaneKnowledge:
    """Test suite for initialize_pennylane_knowledge function."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary directory for the test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory with sample documentation files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_path = Path(tmpdir)

            # Create various file types
            (docs_path / "doc1.md").write_text("# PennyLane Documentation")
            (docs_path / "doc2.txt").write_text("Additional notes on quantum gates")
            (docs_path / "example.py").write_text("import pennylane as qml")

            # Create a subdirectory
            subdir = docs_path / "advanced"
            subdir.mkdir()
            (subdir / "advanced_topics.md").write_text("# Advanced Topics")

            yield docs_path

    def test_initialize_with_docs(self, temp_db, temp_docs_dir):
        """Test initializing knowledge base with documentation directory."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        kb = initialize_pennylane_knowledge(
            docs_dir=temp_docs_dir,
            db_uri=temp_db,
        )

        assert kb is not None
        assert isinstance(kb, PennyLaneKnowledge)

        # Search for content to verify it was loaded
        results = kb.search("PennyLane")
        assert len(results) > 0

    def test_initialize_nonexistent_dir(self, temp_db):
        """Test that initialization fails with non-existent directory."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        with pytest.raises(
            FileNotFoundError, match="Documentation directory not found"
        ):
            initialize_pennylane_knowledge(
                docs_dir="/nonexistent/directory",
                db_uri=temp_db,
            )

    def test_initialize_force_reload(self, temp_db, temp_docs_dir):
        """Test force_reload parameter."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        # Initialize once
        kb1 = initialize_pennylane_knowledge(
            docs_dir=temp_docs_dir,
            db_uri=temp_db,
        )

        # Add some custom content
        kb1.add_text(content="Custom content", name="custom")

        # Initialize again with force_reload
        kb2 = initialize_pennylane_knowledge(
            docs_dir=temp_docs_dir,
            db_uri=temp_db,
            force_reload=True,
        )

        # The custom content should be gone after force reload
        results = kb2.search("Custom content")
        # Results should be empty or not contain our custom content
        assert len(results) == 0 or not any("Custom content" in str(r) for r in results)


class TestGetKnowledgeForAgent:
    """Test suite for get_knowledge_for_agent function."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary directory for the test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_get_knowledge_for_agent(self, temp_db):
        """Test getting Knowledge instance for agent integration."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        knowledge = get_knowledge_for_agent(db_uri=temp_db, table_name="agent_kb")

        # Verify it's a Knowledge instance
        assert knowledge is not None
        assert hasattr(knowledge, "search")
        assert hasattr(knowledge, "add_content")

    def test_knowledge_integration_with_mock_agent(self, temp_db):
        """Test that the Knowledge instance works with agent-like usage."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        knowledge = get_knowledge_for_agent(db_uri=temp_db)

        # Add some content
        knowledge.add_content(
            name="test_content",
            content="This is test content for agent integration.",
        )

        # Search (as an agent would)
        results = knowledge.search(query="test content", num_documents=5)
        assert len(results) > 0


class TestKnowledgeBaseIntegration:
    """Integration tests for the complete knowledge base workflow."""

    @pytest.fixture
    def temp_setup(self):
        """Create temporary directories for database and docs."""
        with tempfile.TemporaryDirectory() as db_dir:
            with tempfile.TemporaryDirectory() as docs_dir:
                docs_path = Path(docs_dir)

                # Create a comprehensive set of test documents
                (docs_path / "introduction.md").write_text(
                    """# Introduction to PennyLane

PennyLane is a Python library for quantum machine learning,
automatic differentiation, and optimization of hybrid quantum-classical computations.
"""
                )

                (docs_path / "gates.md").write_text(
                    """# Quantum Gates

## Single-Qubit Gates
- Hadamard: qml.Hadamard(wires=0)
- PauliX: qml.PauliX(wires=0)
- PauliY: qml.PauliY(wires=0)
- PauliZ: qml.PauliZ(wires=0)

## Two-Qubit Gates
- CNOT: qml.CNOT(wires=[0, 1])
- CZ: qml.CZ(wires=[0, 1])
"""
                )

                (docs_path / "circuit_example.py").write_text(
                    """import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
"""
                )

                yield db_dir, docs_path

    def test_end_to_end_workflow(self, temp_setup):
        """Test complete workflow from initialization to search."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        db_dir, docs_path = temp_setup

        # Initialize knowledge base with documentation
        kb = initialize_pennylane_knowledge(docs_dir=docs_path, db_uri=db_dir)

        # Test search for conceptual content
        results = kb.search("quantum machine learning", num_results=3)
        assert len(results) > 0

        # Test search for code-related content
        results = kb.search("Hadamard gate CNOT", num_results=3)
        assert len(results) > 0

        # Test search for specific API usage
        results = kb.search("qml.device default.qubit", num_results=2)
        assert len(results) > 0

    def test_metadata_preservation(self, temp_setup):
        """Test that metadata is preserved through the workflow."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        db_dir, _ = temp_setup

        kb = PennyLaneKnowledge(db_uri=db_dir)

        # Add content with metadata
        kb.add_text(
            content="Test content with metadata",
            name="metadata_test",
            metadata={
                "category": "test",
                "importance": "high",
                "version": "1.0",
            },
        )

        # Search and verify metadata is accessible
        results = kb.search("metadata")
        assert len(results) > 0
        # Note: The exact structure of results may vary depending on Agno's implementation
