"""Demonstration of circuit manipulation features.

This script shows how to use Skadi's circuit manipulation capabilities:
- Transform: Apply PennyLane transforms
- Optimize: Reduce gate count and depth
- Understand: Analyze and explain circuits
- Rewrite: Modify circuits with natural language

Usage:
    uv run python examples/circuit_manipulation_demo.py
"""

from skadi import CircuitGenerator, CircuitManipulator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_transform():
    """Demonstrate circuit transformation."""
    print_section("DEMO 1: Circuit Transformation")

    # Generate a circuit
    generator = CircuitGenerator()
    circuit = generator.generate_circuit("Create a Bell state with extra inverse gates")

    print("Original Circuit:")
    print(circuit.get_visualization())
    print(f"\nOriginal Stats: {circuit.get_resource_summary()}")

    # Apply transformations
    manipulator = CircuitManipulator()

    print("\n--- Applying cancel_inverses transform ---")
    transformed = manipulator.transform(circuit, "cancel_inverses")
    print(transformed.get_visualization())
    print(f"Transformed Stats: {transformed.get_resource_summary()}")

    print("\n--- Applying merge_rotations transform ---")
    transformed2 = manipulator.transform(transformed, "merge_rotations")
    print(f"After merge_rotations: {transformed2.get_resource_summary()}")

    print(
        f"\nTransform History: {len(transformed2.transform_history)} transforms applied"
    )


def demo_optimize():
    """Demonstrate circuit optimization."""
    print_section("DEMO 2: Circuit Optimization")

    # Generate a circuit
    generator = CircuitGenerator()
    circuit = generator.generate_circuit(
        "Create a 3-qubit circuit with Hadamards and CNOTs"
    )

    print("Original Circuit:")
    print(circuit.get_visualization())
    before_stats = circuit.get_resource_summary()
    print("\nBefore Optimization:")
    print(f"  Operations: {before_stats['num_operations']}")
    print(f"  Depth: {before_stats['depth']}")

    # Optimize with different levels
    manipulator = CircuitManipulator()

    for level in ["basic", "default", "aggressive"]:
        print(f"\n--- Optimization Level: {level} ---")
        optimized = manipulator.optimize(circuit, level=level, num_passes=2)
        after_stats = optimized.get_resource_summary()

        improvement = optimized.transform_history[-1].get("improvement", {})

        print("After Optimization:")
        print(
            f"  Operations: {after_stats['num_operations']} "
            f"(reduced by {improvement.get('operations_reduced', 0)})"
        )
        print(
            f"  Depth: {after_stats['depth']} "
            f"(reduced by {improvement.get('depth_reduced', 0)})"
        )

    # Get optimization report
    optimized = manipulator.optimize(circuit, level="aggressive")
    report = manipulator.get_optimization_report(optimized)
    print("\n--- Optimization Report ---")
    print(report["summary"])


def demo_understand():
    """Demonstrate circuit analysis."""
    print_section("DEMO 3: Circuit Understanding")

    # Generate a circuit
    generator = CircuitGenerator()
    circuit = generator.generate_circuit("Create a GHZ state for 3 qubits")

    print("Circuit to Analyze:")
    print(circuit.get_visualization())

    # Analyze the circuit
    manipulator = CircuitManipulator()
    analysis = manipulator.understand(circuit, include_explanation=True, verbose=True)

    print("\n--- Circuit Analysis ---")
    print(f"Description: {analysis['description']}")
    print(f"\nComplexity Level: {analysis['complexity']['level']}")
    print(f"Total Operations: {analysis['specs']['num_operations']}")
    print(f"Circuit Depth: {analysis['specs']['depth']}")
    print(f"Qubits: {analysis['specs']['num_wires']}")
    print(f"Entangling Gates: {analysis['complexity']['entangling_gates']}")

    print("\n--- Gate Analysis ---")
    gate_analysis = analysis["gate_analysis"]
    print(f"Single-qubit gates: {gate_analysis['single_qubit_count']}")
    print(f"Multi-qubit gates: {gate_analysis['multi_qubit_count']}")
    print(f"Gate types: {gate_analysis['gate_types']}")

    if analysis.get("explanation"):
        print("\n--- LLM-Generated Explanation ---")
        print(
            analysis["explanation"][:500] + "..."
            if len(analysis["explanation"]) > 500
            else analysis["explanation"]
        )


def demo_rewrite():
    """Demonstrate circuit rewriting."""
    print_section("DEMO 4: Circuit Rewriting")

    # Generate a circuit
    generator = CircuitGenerator()
    circuit = generator.generate_circuit("Create a simple Bell state")

    print("Original Circuit:")
    print(circuit.get_visualization())
    print(f"\nOriginal Code:\n{circuit.code}")

    # Rewrite the circuit
    manipulator = CircuitManipulator()

    modification = "Add a phase gate before the CNOT"
    print("\n--- Rewriting Circuit ---")
    print(f"Modification Request: {modification}")

    rewritten = manipulator.rewrite(circuit, modification)

    print("\nRewritten Circuit:")
    print(rewritten.get_visualization())
    print(f"\nRewritten Code:\n{rewritten.code}")

    print(f"\nTransform History: {len(rewritten.transform_history)} modifications")


def demo_workflow():
    """Demonstrate complete manipulation workflow."""
    print_section("DEMO 5: Complete Workflow")

    # Generate → Analyze → Optimize → Compare
    generator = CircuitGenerator()
    manipulator = CircuitManipulator()

    print("Step 1: Generate Circuit")
    circuit = generator.generate_circuit(
        "Create a quantum Fourier transform circuit for 2 qubits"
    )
    print(circuit.get_visualization())

    print("\nStep 2: Analyze Original")
    analysis1 = manipulator.understand(circuit, include_explanation=False)
    print(f"  Operations: {analysis1['specs']['num_operations']}")
    print(f"  Depth: {analysis1['specs']['depth']}")

    print("\nStep 3: Optimize")
    optimized = manipulator.optimize(circuit, level="aggressive", num_passes=3)
    print(
        f"  Operations after optimization: {optimized.get_resource_summary()['num_operations']}"
    )
    print(f"  Depth after optimization: {optimized.get_resource_summary()['depth']}")

    print("\nStep 4: Compare Original vs Optimized")
    comparison = manipulator.compare_circuits(
        circuit, optimized, names=("Original", "Optimized")
    )
    print(f"  Difference in operations: {comparison['differences']['operations']}")
    print(f"  Difference in depth: {comparison['differences']['depth']}")

    print("\nStep 5: Get Optimization Report")
    report = manipulator.get_optimization_report(optimized)
    print(f"  {report['summary']}")


def main():
    """Run all manipulation demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CIRCUIT MANIPULATION DEMO" + " " * 33 + "║")
    print(
        "║" + " " * 15 + "Transform • Optimize • Understand • Rewrite" + " " * 20 + "║"
    )
    print("╚" + "=" * 78 + "╝")

    try:
        # Run all demos
        demo_transform()
        demo_optimize()
        demo_understand()
        demo_rewrite()
        demo_workflow()

        print("\n" + "=" * 80)
        print("  ALL DEMOS COMPLETE")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("1. Transform: Apply PennyLane's built-in transforms to circuits")
        print("2. Optimize: Reduce gate count and depth with optimization pipelines")
        print("3. Understand: Analyze circuit structure and generate explanations")
        print("4. Rewrite: Modify circuits using natural language requests")
        print("5. Complete workflows: Chain operations for complex manipulations")
        print("=" * 80)

    except Exception as e:
        print(f"\nError during demo: {e}")
        print("\nMake sure you have set OPENROUTER_API_KEY environment variable")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
