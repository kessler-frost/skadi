"""Demonstration of circuit manipulation features.

This script shows how to use Skadi's circuit manipulation capabilities:
- Optimize: Reduce gate count and depth
- Understand: Analyze and explain circuits
- Rewrite: Modify circuits with natural language
- Compare: Compare two circuit versions

Usage:
    uv run python examples/circuit_manipulation_demo.py
"""

from skadi import CircuitGenerator, CircuitManipulator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_header():
    """Print demo header."""
    print("╔" + "=" * 78 + "╗")
    print("║" + "CIRCUIT MANIPULATION DEMO".center(78) + "║")
    print("║" + "Optimize • Understand • Rewrite • Compare".center(78) + "║")
    print("╚" + "=" * 78 + "╝")


def demo_optimization():
    """Demonstrate circuit optimization."""
    print_section("DEMO 1: Circuit Optimization")

    # Generate a circuit
    generator = CircuitGenerator()
    circuit = generator.generate_circuit(
        "Create a 3-qubit GHZ state with some extra rotations"
    )

    print("Original Circuit:")
    print(circuit.get_visualization())
    print(f"\nOriginal Stats: {circuit.get_resource_summary()}")

    # Apply optimization
    manipulator = CircuitManipulator()

    print("\n--- Applying aggressive optimization ---")
    optimized = manipulator.optimize(circuit, level="aggressive", num_passes=2)
    print(optimized.get_visualization())
    print(f"Optimized Stats: {optimized.get_resource_summary()}")

    # Get optimization report
    report = manipulator.get_optimization_report(optimized)
    print(f"\nOptimization Report:")
    print(f"  Optimizations applied: {report['optimizations_applied']}")
    if report.get("total_improvement"):
        print(f"  Total operations reduced: {report['total_improvement'].get('total_operations_reduced', 0)}")
        print(f"  Total depth reduced: {report['total_improvement'].get('total_depth_reduced', 0)}")
    if report.get("summary"):
        print(f"\nSummary: {report['summary']}")


def demo_understanding():
    """Demonstrate circuit analysis."""
    print_section("DEMO 2: Circuit Understanding")

    generator = CircuitGenerator()
    circuit = generator.generate_circuit("Create a Bell state")

    manipulator = CircuitManipulator()

    print("Analyzing circuit...")
    analysis = manipulator.understand(circuit, include_explanation=True, verbose=True)

    print(f"\nComplexity: {analysis['complexity']['level']}")
    print(f"Operations: {analysis['specs']['num_operations']}")
    print(f"Depth: {analysis['specs']['depth']}")
    print(f"Qubits: {analysis['specs']['num_wires']}")

    if analysis.get("explanation"):
        print(f"\nExplanation:")
        print(analysis["explanation"])


def demo_rewrite():
    """Demonstrate circuit rewriting."""
    print_section("DEMO 3: Circuit Rewriting")

    generator = CircuitGenerator()
    circuit = generator.generate_circuit("Create a simple superposition circuit")

    print("Original Circuit:")
    print(circuit.get_visualization())

    manipulator = CircuitManipulator()

    print("\n--- Rewriting with natural language ---")
    modified = manipulator.rewrite(circuit, "Add a phase gate after the Hadamard")

    print("\nModified Circuit:")
    print(modified.get_visualization())

    print(f"\nOriginal operations: {circuit.get_resource_summary()['num_operations']}")
    print(f"Modified operations: {modified.get_resource_summary()['num_operations']}")


def demo_comparison():
    """Demonstrate circuit comparison."""
    print_section("DEMO 4: Circuit Comparison")

    generator = CircuitGenerator()
    manipulator = CircuitManipulator()

    # Create original circuit
    original = generator.generate_circuit("Create a 2-qubit Bell state")

    # Optimize it
    optimized = manipulator.optimize(original, level="aggressive")

    print("Comparing circuits...")
    comparison = manipulator.compare_circuits(
        original, optimized, names=("Original", "Optimized")
    )

    print(f"\nOriginal Circuit:")
    print(f"  Operations: {comparison['circuit1']['operations']}")
    print(f"  Depth: {comparison['circuit1']['depth']}")

    print(f"\nOptimized Circuit:")
    print(f"  Operations: {comparison['circuit2']['operations']}")
    print(f"  Depth: {comparison['circuit2']['depth']}")

    print(f"\nDifferences:")
    print(f"  Operations: {comparison['differences']['operations']}")
    print(f"  Depth: {comparison['differences']['depth']}")


def main():
    """Run all demos."""
    try:
        print_header()
        demo_optimization()
        demo_understanding()
        demo_rewrite()
        demo_comparison()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE".center(80))
        print("=" * 80)

    except Exception as e:
        print(f"\nError during demo: {e}")
        print("\nMake sure you have set OPENROUTER_API_KEY environment variable")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
