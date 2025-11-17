"""Tests for circuit generator functionality."""

import pytest

from skadi.core.circuit_generator import CircuitGenerator
from skadi.engine.llm_client import LLMClient


class TestLLMClient:
    """Tests for LLM client."""

    def test_init_without_api_key_raises_error(self, monkeypatch):
        """Test that initializing without API key raises ValueError."""
        # Clear the environment variable
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        # Mock the settings to return None for openrouter_api_key
        from skadi import config

        monkeypatch.setattr(config.settings, "openrouter_api_key", None)

        with pytest.raises(ValueError, match="OpenRouter API key not found"):
            LLMClient()

    def test_init_with_api_key(self):
        """Test that initializing with API key works."""
        client = LLMClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model_id == "anthropic/claude-haiku-4.5"


class TestCircuitGenerator:
    """Tests for circuit generator."""

    def test_init(self):
        """Test circuit generator initialization."""
        generator = CircuitGenerator(api_key="test_key")
        assert generator.llm_client is not None
        assert isinstance(generator.llm_client, LLMClient)

    def test_validate_code_empty(self):
        """Test validation fails for empty code."""
        generator = CircuitGenerator(api_key="test_key")

        with pytest.raises(ValueError, match="Generated code is empty"):
            generator._validate_code("")

    def test_validate_code_missing_import(self):
        """Test validation fails when pennylane import is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
def circuit():
    return None
"""

        with pytest.raises(ValueError, match="must import pennylane"):
            generator._validate_code(code)

    def test_validate_code_missing_device(self):
        """Test validation fails when device creation is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

def circuit():
    return qml.state()
"""

        with pytest.raises(ValueError, match="must create a quantum device"):
            generator._validate_code(code)

    def test_validate_code_missing_qnode(self):
        """Test validation fails when QNode decorator is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

def circuit():
    return qml.state()
"""

        with pytest.raises(ValueError, match="must use @qml.qnode decorator"):
            generator._validate_code(code)

    def test_validate_code_valid(self):
        """Test validation passes for valid code."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
"""

        # Should not raise any exception
        generator._validate_code(code)

    def test_execute_code_valid(self):
        """Test executing valid circuit code."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    return qml.state()
"""

        circuit = generator._execute_code(code)
        assert callable(circuit)

        # Execute the circuit
        result = circuit()
        assert result is not None

    def test_execute_code_invalid_syntax(self):
        """Test executing code with syntax error."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml
def circuit(
    return None
"""

        with pytest.raises(ValueError, match="Syntax error"):
            generator._execute_code(code)
