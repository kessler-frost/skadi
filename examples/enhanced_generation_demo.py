"""
Demo of enhanced circuit generation with dual knowledge system.

This example demonstrates how the CircuitGenerator uses both:
1. PennyLaneKnowledge: Conceptual understanding of quantum algorithms
2. Context7Client: API-specific documentation and syntax

The knowledge sources work together to improve circuit generation accuracy.
"""

from skadi.config import settings
from skadi.core.circuit_generator import CircuitGenerator

# Initialize generator with dual knowledge system enabled
generator = CircuitGenerator(
    api_key=settings.openrouter_api_key,
    model="anthropic/claude-haiku-4.5",
    use_knowledge=True,  # Enable knowledge augmentation
    use_pennylane_kb=True,  # Use PennyLane knowledge base
    use_context7=True,  # Use Context7 API docs
)


def demo_bell_state():
    """Generate a Bell state circuit."""
    print("=" * 80)
    print("DEMO 1: Bell State Generation")
    print("=" * 80)

    description = "Create a Bell state circuit that maximally entangles two qubits"

    # Get knowledge stats to see what's being retrieved
    stats = generator.get_knowledge_stats(description)
    print("\nKnowledge Retrieval Statistics:")
    print(f"  - Knowledge enabled: {stats['knowledge_enabled']}")
    print(f"  - Sources: {', '.join(stats.get('sources_enabled', []))}")
    print(f"  - PennyLane KB results: {stats.get('pennylane_kb_results', 0)}")
    print(f"  - Context7 API results: {stats.get('context7_results', 0)}")

    # Generate the circuit
    print(f"\nGenerating circuit for: '{description}'")
    circuit, code = generator.generate_with_code(description)

    print("\nGenerated Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)

    # Execute the circuit
    print("\nExecuting circuit...")
    result = circuit()
    print(f"Result shape: {result.shape}")
    print(f"Result (first 4 elements): {result[:4]}")


def demo_grover():
    """Generate a Grover diffusion operator."""
    print("\n" + "=" * 80)
    print("DEMO 2: Grover Diffusion Operator")
    print("=" * 80)

    description = "Create a Grover diffusion operator for 3 qubits"

    stats = generator.get_knowledge_stats(description)
    print("\nKnowledge Retrieval Statistics:")
    print(f"  - Knowledge enabled: {stats['knowledge_enabled']}")
    print(f"  - Sources: {', '.join(stats.get('sources_enabled', []))}")
    print(f"  - PennyLane KB results: {stats.get('pennylane_kb_results', 0)}")
    print(f"  - Context7 API results: {stats.get('context7_results', 0)}")

    print(f"\nGenerating circuit for: '{description}'")
    circuit, code = generator.generate_with_code(description)

    print("\nGenerated Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)


def demo_comparison():
    """Compare generation with and without knowledge."""
    print("\n" + "=" * 80)
    print("DEMO 3: Knowledge System Comparison")
    print("=" * 80)

    description = "Create a quantum circuit with superposition and entanglement"

    print(f"\nDescription: '{description}'")

    # Generate WITHOUT knowledge
    print("\n--- WITHOUT Knowledge Augmentation ---")
    _, code_without = generator.generate_with_code(description, use_knowledge=False)
    print(code_without)

    # Generate WITH knowledge
    print("\n--- WITH Knowledge Augmentation ---")
    _, code_with = generator.generate_with_code(description, use_knowledge=True)
    print(code_with)

    print("\n" + "=" * 80)
    print("Notice how the knowledge-enhanced version may include:")
    print("- More accurate gate choices based on conceptual understanding")
    print("- Proper API syntax from Context7 documentation")
    print("- Better structured code following quantum computing patterns")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ENHANCED CIRCUIT GENERATION DEMO" + " " * 26 + "║")
    print("║" + " " * 18 + "Dual Knowledge System in Action" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # Run demos
        demo_bell_state()
        demo_grover()
        demo_comparison()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("1. PennyLaneKnowledge provides conceptual understanding of algorithms")
        print("2. Context7Client provides accurate API syntax and examples")
        print("3. Both sources work together to enhance circuit generation")
        print("4. Knowledge can be toggled on/off per request or globally")
        print("=" * 80)

    except Exception as e:
        print(f"\nError during demo: {e}")
        print("\nMake sure you have set:")
        print("  - OPENROUTER_API_KEY environment variable")
