"""Circuit execution with backend binding."""

import re
from typing import Any

import pennylane as qml

from skadi.backends.base import Backend
from skadi.backends.registry import BackendRegistry
from skadi.core.circuit_representation import CircuitRepresentation


class CircuitExecutor:
    """Executes circuits on specified backends."""

    def __init__(self, registry: BackendRegistry | None = None) -> None:
        self.registry = registry or BackendRegistry()

    def bind_circuit_to_device(
        self,
        circuit: CircuitRepresentation,
        backend: Backend,
        shots: int | None = None,
    ) -> CircuitRepresentation:
        """Bind a circuit to a specific backend device.

        Creates a new QNode using the backend's device while preserving
        the circuit's quantum function.
        """
        specs = circuit.get_specs()
        num_wires = specs.get("num_device_wires", 2)

        device = backend.create_device(wires=num_wires, shots=shots)

        # Extract the quantum function from existing code
        quantum_func = self._extract_quantum_function(circuit.code)

        # Create new QNode with the backend device
        new_qnode = qml.QNode(quantum_func, device)

        # Create new representation with updated device
        new_circuit = circuit.clone(qnode=new_qnode)
        new_circuit.metadata["backend"] = backend.get_info().name
        new_circuit.metadata["shots"] = shots

        return new_circuit

    def _extract_quantum_function(self, code: str) -> Any:
        """Extract the raw quantum function from circuit code.

        Parses the code to find the circuit function and returns it
        without the @qml.qnode decorator.
        """
        # Remove the @qml.qnode decorator line
        modified_code = re.sub(r"@qml\.qnode\([^)]+\)\s*\n", "", code)

        # Remove device creation line
        modified_code = re.sub(
            r"dev\s*=\s*qml\.device\([^)]+\)\s*\n", "", modified_code
        )

        namespace: dict[str, Any] = {"qml": qml, "pennylane": qml}
        exec(modified_code, namespace)

        return namespace.get("circuit")

    def execute(
        self,
        circuit: CircuitRepresentation,
        backend_name: str,
        shots: int | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a circuit on the specified backend."""
        backend = self.registry.get(backend_name)
        if not backend:
            available = [s.info.name for s in self.registry.list_available()]
            msg = f"Backend '{backend_name}' not found. Available: {available}"
            raise ValueError(msg)

        bound_circuit = self.bind_circuit_to_device(circuit, backend, shots)
        return bound_circuit.qnode(**kwargs)
