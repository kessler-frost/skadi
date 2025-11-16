"""Functional tests for circuit generation end-to-end."""

import os
from pathlib import Path

import numpy as np
import pytest
from dotenv import load_dotenv

from skadi import CircuitGenerator

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
load_dotenv(env_file)


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - skipping functional tests",
)
class TestCircuitGenerationFunctional:
    """End-to-end functional tests for circuit generation."""

    @pytest.fixture(scope="class")
    def generator(self):
        """Create a circuit generator instance."""
        return CircuitGenerator()

    def test_bell_state_generation(self, generator):
        """Test generating a Bell state circuit from natural language.

        A Bell state should produce the state |Φ+⟩ = (|00⟩ + |11⟩)/√2
        which has amplitudes [0.707, 0, 0, 0.707] approximately.
        """
        description = "Create a Bell state circuit"

        # Generate the circuit
        circuit, code = generator.generate_with_code(description)

        # Verify code was generated
        assert code is not None
        assert "pennylane" in code or "qml" in code
        assert "Hadamard" in code or "hadamard" in code.lower()
        assert "CNOT" in code or "cnot" in code.lower()

        # Execute the circuit
        result = circuit()

        # Verify the Bell state
        # Expected: [0.707, 0, 0, 0.707] (approximately)
        assert result is not None
        assert len(result) == 4

        # Check that we have the correct Bell state amplitudes
        expected = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])
        np.testing.assert_allclose(np.abs(result), np.abs(expected), atol=1e-5)

    def test_superposition_generation(self, generator):
        """Test generating a superposition circuit from natural language.

        A single-qubit superposition using Hadamard should produce
        equal probabilities [0.5, 0.5] when measured.
        """
        description = (
            "Create a circuit that puts a single qubit in "
            "superposition using a Hadamard gate"
        )

        # Generate the circuit
        circuit, code = generator.generate_with_code(description)

        # Verify code was generated
        assert code is not None
        assert "pennylane" in code or "qml" in code
        assert "Hadamard" in code or "hadamard" in code.lower()

        # Execute the circuit
        result = circuit()

        # Verify the result - should be either state vector or probabilities
        assert result is not None

        # If it's a complex-valued state vector, check amplitudes
        if np.iscomplexobj(result):
            expected_state = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
            np.testing.assert_allclose(np.abs(result), expected_state, atol=1e-5)
        # If it's probabilities (real-valued), check equal probabilities
        else:
            expected_probs = np.array([0.5, 0.5])
            np.testing.assert_allclose(result, expected_probs, atol=1e-5)

    def test_generated_circuit_is_callable(self, generator):
        """Test that generated circuits are callable functions."""
        description = "Create a Bell state circuit"

        circuit = generator.generate(description)

        # Verify it's callable
        assert callable(circuit)

        # Verify it can be executed multiple times
        result1 = circuit()
        result2 = circuit()

        # Results should be identical
        np.testing.assert_array_equal(result1, result2)
