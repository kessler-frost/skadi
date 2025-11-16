"""Example script demonstrating natural language to PennyLane circuit generation."""

import os
from dotenv import load_dotenv

from skadi.core.circuit_generator import CircuitGenerator


def main():
    """Demonstrate circuit generation from natural language."""
    # Load environment variables from .env file
    load_dotenv()

    # Verify API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenRouter API key:")
        print("OPENROUTER_API_KEY=your_api_key_here")
        return

    # Initialize the circuit generator
    print("Initializing circuit generator...")
    generator = CircuitGenerator()

    # Example 1: Generate a Bell state circuit
    print("\n" + "=" * 70)
    print("Example: Generating a Bell state circuit")
    print("=" * 70)

    description = "Create a Bell state circuit"
    print(f"\nDescription: {description}")

    try:
        # Generate the circuit and get the code
        circuit, code = generator.generate_with_code(description)

        print("\nGenerated Code:")
        print("-" * 70)
        print(code)
        print("-" * 70)

        # Execute the circuit
        print("\nExecuting circuit...")
        result = circuit()

        print("\nCircuit output:")
        print(result)

        # Display circuit structure
        print("\nCircuit drawer output:")
        print(circuit.qtape)

    except Exception as e:
        print(f"\nError: {str(e)}")

    # Example 2: Another simple circuit
    print("\n" + "=" * 70)
    print("Example: Generating a simple superposition circuit")
    print("=" * 70)

    description = "Create a circuit that puts a single qubit in superposition using a Hadamard gate"
    print(f"\nDescription: {description}")

    try:
        circuit, code = generator.generate_with_code(description)

        print("\nGenerated Code:")
        print("-" * 70)
        print(code)
        print("-" * 70)

        print("\nExecuting circuit...")
        result = circuit()

        print("\nCircuit output:")
        print(result)

    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
