"""Example demonstrating how to use the PennyLane Knowledge Base.

This script shows:
1. How to initialize the knowledge base
2. How to add different types of content
3. How to search for information
4. How to integrate with Agno agents

NOTE: Uses FastEmbed for local embeddings (no API key required).
      The embedding model (~69 MB) downloads automatically on first use.
"""

from pathlib import Path

from dotenv import load_dotenv

from skadi.engine.knowledge_base import (
    PennyLaneKnowledge,
    get_knowledge_for_agent,
    initialize_pennylane_knowledge,
)

# Load environment variables
load_dotenv()


def example_basic_usage():
    """Basic usage example: create, add content, and search."""
    print("\n=== Basic Knowledge Base Usage ===\n")

    # Initialize knowledge base
    kb = PennyLaneKnowledge(
        db_uri="tmp/lancedb",
        table_name="example_kb",
    )

    # Add some text content
    print("Adding content to knowledge base...")
    kb.add_text(
        content="""
        The Hadamard gate is a fundamental quantum gate that creates superposition.
        It transforms the |0⟩ state into (|0⟩ + |1⟩)/√2 and |1⟩ into (|0⟩ - |1⟩)/√2.
        In PennyLane, it's used as: qml.Hadamard(wires=0)
        """,
        name="hadamard_gate_info",
        metadata={"topic": "quantum_gates", "difficulty": "beginner"},
    )

    kb.add_text(
        content="""
        Quantum entanglement is a phenomenon where quantum states of two or more
        particles are correlated. The CNOT gate is commonly used to create entanglement.
        A Bell state is a maximally entangled state created using Hadamard and CNOT gates.
        """,
        name="entanglement_info",
        metadata={"topic": "entanglement", "difficulty": "intermediate"},
    )

    kb.add_text(
        content="""
        PennyLane's qml.qnode decorator converts a quantum function into a quantum node.
        It requires a device to be specified and returns measurement results when called.
        Example: @qml.qnode(dev) where dev is a quantum device.
        """,
        name="qnode_decorator_info",
        metadata={"topic": "pennylane_api", "difficulty": "beginner"},
    )

    # Search for information
    print("\nSearching for 'Hadamard superposition'...")
    results = kb.search("Hadamard superposition", num_results=2)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result}")

    print("\n\nSearching for 'entanglement Bell state'...")
    results = kb.search("entanglement Bell state", num_results=2)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result}")


def example_file_loading():
    """Example: loading documentation from files."""
    print("\n\n=== Loading Files into Knowledge Base ===\n")

    # Create a temporary file with documentation
    temp_dir = Path("tmp/example_docs")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create a sample markdown file
    sample_doc = temp_dir / "quantum_circuits.md"
    sample_doc.write_text(
        """# Quantum Circuits in PennyLane

## Basic Circuit Structure

A quantum circuit in PennyLane consists of:
1. Device initialization: `dev = qml.device("default.qubit", wires=n)`
2. Quantum function with @qml.qnode decorator
3. Quantum operations (gates)
4. Measurements

## Example: Bell State Circuit

```python
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
```

This creates a maximally entangled Bell state.
"""
    )

    # Initialize knowledge base and load the file
    kb = PennyLaneKnowledge(db_uri="tmp/lancedb", table_name="file_example_kb")

    print(f"Loading documentation from {sample_doc}...")
    kb.add_file(
        file_path=sample_doc,
        metadata={"source": "example_docs", "format": "markdown"},
    )

    # Search for content from the file
    print("\nSearching for 'Bell state circuit example'...")
    results = kb.search("Bell state circuit example", num_results=2)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result}")


def example_initialization_from_directory():
    """Example: initialize knowledge base from a documentation directory."""
    print("\n\n=== Initializing from Documentation Directory ===\n")

    # Check if the pennylane_docs directory exists
    docs_dir = Path("data/pennylane_docs")

    if not docs_dir.exists() or not any(docs_dir.iterdir()):
        print(
            f"Note: {docs_dir} is empty or doesn't exist. "
            "This example requires scraped PennyLane documentation."
        )
        print("Skipping this example...")
        return

    print(f"Initializing knowledge base from {docs_dir}...")
    kb = initialize_pennylane_knowledge(
        docs_dir=docs_dir,
        db_uri="tmp/lancedb",
        force_reload=False,  # Don't reload if already initialized
    )

    # Test search on loaded documentation
    print("\nSearching loaded documentation for 'gradient descent optimization'...")
    results = kb.search("gradient descent optimization", num_results=3)

    if results:
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {result}")
    else:
        print("No results found (documentation may not contain this topic)")


def example_agent_integration():
    """Example: using knowledge base with an Agno agent."""
    print("\n\n=== Agent Integration Example ===\n")

    # First, populate some knowledge
    kb = PennyLaneKnowledge(db_uri="tmp/lancedb", table_name="agent_kb")

    kb.add_text(
        content="""
        PennyLane supports various quantum devices including simulators and hardware:
        - default.qubit: Fast CPU simulator
        - lightning.qubit: Optimized CPU simulator
        - default.mixed: Density matrix simulator for mixed states
        - qiskit.aer: IBM Qiskit Aer simulator
        - Hardware providers: IBM, Rigetti, IonQ, and more
        """,
        name="pennylane_devices",
    )

    kb.add_text(
        content="""
        Variational quantum algorithms (VQAs) combine quantum circuits with
        classical optimization. PennyLane makes it easy to build VQAs using:
        - Parameterized quantum circuits (ansätze)
        - Automatic differentiation for gradient computation
        - Integration with machine learning frameworks (PyTorch, TensorFlow, JAX)
        """,
        name="variational_algorithms",
    )

    # Get the Knowledge instance for agent integration
    knowledge = get_knowledge_for_agent(db_uri="tmp/lancedb", table_name="agent_kb")

    print("Knowledge base ready for agent integration!")
    print("\nYou can now use this knowledge with an Agno agent:")
    print(
        """
from agno.agent import Agent
from agno.models.openrouter import OpenRouter

agent = Agent(
    model=OpenRouter(id="anthropic/claude-haiku-4.5"),
    knowledge=knowledge,
    instructions=[
        "You are a quantum computing expert.",
        "Search your knowledge base before answering questions.",
        "Provide accurate, detailed answers about PennyLane."
    ],
)

# Now the agent can answer questions using the knowledge base
response = agent.run("What devices does PennyLane support?")
    """
    )

    # Demonstrate direct search
    print("\nDirect search example:")
    results = knowledge.search("variational quantum algorithms", num_documents=2)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result}")


def main():
    """Run all examples."""
    print("PennyLane Knowledge Base Examples")
    print("=" * 50)
    print("Using FastEmbed for local embeddings (no API key required)")
    print("Model will be downloaded automatically on first use (~69 MB)")
    print()

    try:
        # Run examples
        example_basic_usage()
        example_file_loading()
        example_initialization_from_directory()
        example_agent_integration()

        print("\n\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
