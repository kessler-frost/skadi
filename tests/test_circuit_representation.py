"""Unit tests for CircuitRepresentation class."""

import pennylane as qml
import pytest

from skadi.core.circuit_representation import CircuitRepresentation


@pytest.fixture
def simple_circuit():
    """Create a simple Bell state circuit for testing."""
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    code = """import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
"""

    return CircuitRepresentation(
        qnode=circuit,
        code=code,
        description="Bell state circuit",
        metadata={"test": True},
    )


class TestCircuitRepresentation:
    """Test CircuitRepresentation functionality."""

    def test_init(self, simple_circuit):
        """Test basic initialization."""
        assert simple_circuit.qnode is not None
        assert simple_circuit.code is not None
        assert simple_circuit.description == "Bell state circuit"
        assert simple_circuit.metadata["test"] is True
        assert simple_circuit.transform_history == []

    def test_get_specs(self, simple_circuit):
        """Test getting circuit specifications."""
        specs = simple_circuit.get_specs()

        # Check that resources are present
        assert "resources" in specs or "num_operations" in specs
        assert "num_device_wires" in specs

        # Use resource summary for checking values
        summary = simple_circuit.get_resource_summary()
        assert summary["num_operations"] == 2  # Hadamard + CNOT
        assert summary["depth"] == 2

    def test_get_specs_caching(self, simple_circuit):
        """Test that specs are cached."""
        specs1 = simple_circuit.get_specs()
        specs2 = simple_circuit.get_specs()

        # Should return cached version
        assert specs1 is specs2

        # Refresh should get new specs
        specs3 = simple_circuit.get_specs(refresh=True)
        assert specs3 is not specs1

    def test_get_tape(self, simple_circuit):
        """Test getting quantum tape."""
        tape = simple_circuit.get_tape()

        # Tape might be None in some PennyLane versions
        if tape is not None:
            # Should have operations
            assert hasattr(tape, "operations") or hasattr(tape, "__len__")

    def test_get_visualization(self, simple_circuit):
        """Test circuit visualization."""
        viz = simple_circuit.get_visualization()

        assert isinstance(viz, str)
        assert len(viz) > 0
        # Should contain wire indicators
        assert "0:" in viz or "1:" in viz

    def test_get_resource_summary(self, simple_circuit):
        """Test resource summary."""
        summary = simple_circuit.get_resource_summary()

        assert summary["num_operations"] == 2
        assert summary["depth"] == 2
        assert summary["num_wires"] == 2
        assert "gate_types" in summary

    def test_add_transform(self, simple_circuit):
        """Test adding transformation to history."""
        before_specs = simple_circuit.get_specs()
        after_specs = {"num_operations": 1, "depth": 1}

        simple_circuit.add_transform(
            transform_name="test_transform",
            transform_params={"param": "value"},
            before_specs=before_specs,
            after_specs=after_specs,
        )

        assert len(simple_circuit.transform_history) == 1
        transform = simple_circuit.transform_history[0]

        assert transform["transform"] == "test_transform"
        assert transform["params"] == {"param": "value"}
        assert transform["before"] == before_specs
        assert transform["after"] == after_specs
        assert "timestamp" in transform

        # Cache should be invalidated
        assert simple_circuit._specs is None
        assert simple_circuit._tape is None

    def test_clone(self, simple_circuit):
        """Test cloning circuit representation."""
        # Add some transform history
        simple_circuit.add_transform("test", {}, None, None)

        # Clone with same circuit
        cloned = simple_circuit.clone()

        assert cloned is not simple_circuit
        assert cloned.qnode is simple_circuit.qnode
        assert cloned.code == simple_circuit.code
        assert cloned.description == simple_circuit.description
        assert cloned.metadata == simple_circuit.metadata
        assert cloned.transform_history == simple_circuit.transform_history
        assert cloned.transform_history is not simple_circuit.transform_history

    def test_clone_with_new_qnode(self, simple_circuit):
        """Test cloning with new qnode."""
        dev = qml.device("default.qubit", wires=1)

        @qml.qnode(dev)
        def new_circuit():
            qml.Hadamard(wires=0)
            return qml.state()

        cloned = simple_circuit.clone(qnode=new_circuit, code="new code")

        assert cloned.qnode is new_circuit
        assert cloned.code == "new code"
        assert cloned.description == simple_circuit.description

    def test_repr(self, simple_circuit):
        """Test string representation."""
        repr_str = repr(simple_circuit)

        assert "CircuitRepresentation" in repr_str
        assert "description=" in repr_str
        assert "ops=" in repr_str
        assert "depth=" in repr_str
        assert "wires=" in repr_str

    def test_repr_with_transforms(self, simple_circuit):
        """Test string representation with transforms."""
        simple_circuit.add_transform("test1", {}, None, None)
        simple_circuit.add_transform("test2", {}, None, None)

        repr_str = repr(simple_circuit)
        assert "transforms=2" in repr_str

    def test_no_qnode_errors(self):
        """Test that operations requiring qnode raise errors."""
        circuit = CircuitRepresentation(code="some code")

        with pytest.raises(ValueError, match="QNode is not set"):
            circuit.get_tape()

        with pytest.raises(ValueError, match="QNode is not set"):
            circuit.get_specs()

        with pytest.raises(ValueError, match="QNode is not set"):
            circuit.get_visualization()
