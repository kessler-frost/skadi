"""Tests for circuit generator functionality."""

import pytest

from skadi.core.circuit_generator import CircuitGenerator
from skadi.engine.llm_client import LLMClient


class TestLLMClient:
    """Tests for LLM client."""

    def test_init_without_api_key_raises_error(self, monkeypatch):
        """Test that initializing without API key raises ValueError."""
        # Clear the environment variable
        monkeypatch.delenv("SKADI_API_KEY", raising=False)

        # Mock the settings to return None for skadi_api_key
        from skadi import config

        monkeypatch.setattr(config.settings, "skadi_api_key", None)

        with pytest.raises(ValueError, match="API key not found"):
            LLMClient()

    def test_init_with_api_key(self):
        """Test that initializing with API key works."""
        client = LLMClient(api_key="test_key")
        assert client.api_key == "test_key"
        # Model should be set (either from settings or default)
        assert client.model_id is not None

    def test_init_with_custom_model(self):
        """Test that initializing with custom model works."""
        client = LLMClient(api_key="test_key", model="custom/model")
        assert client.api_key == "test_key"
        assert client.model_id == "custom/model"


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

        error = generator._try_validate_code("")
        assert error is not None
        assert "empty" in error.lower()

    def test_validate_code_missing_import(self):
        """Test validation fails when pennylane import is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
def circuit():
    return None
"""

        error = generator._try_validate_code(code)
        assert error is not None
        assert "pennylane" in error.lower()

    def test_validate_code_missing_device(self):
        """Test validation fails when device creation is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

def circuit():
    return qml.state()
"""

        error = generator._try_validate_code(code)
        assert error is not None
        assert "device" in error.lower()

    def test_validate_code_missing_qnode(self):
        """Test validation fails when QNode decorator is missing."""
        generator = CircuitGenerator(api_key="test_key")

        code = """
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

def circuit():
    return qml.state()
"""

        error = generator._try_validate_code(code)
        assert error is not None
        assert "qnode" in error.lower()

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

        # Should return None (no error)
        error = generator._try_validate_code(code)
        assert error is None

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

        circuit, error = generator._try_execute_code(code)
        assert error is None
        assert circuit is not None
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

        circuit, error = generator._try_execute_code(code)
        assert circuit is None
        assert error is not None
        assert "syntax" in error.lower()
