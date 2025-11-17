"""Visualization helpers for quantum circuits."""

import inspect

import pennylane as qml

from skadi.core.circuit_representation import CircuitRepresentation


def visualize_circuit(circuit_repr: CircuitRepresentation) -> str:
    """Generate ASCII circuit diagram from a CircuitRepresentation.

    Uses PennyLane's qml.draw() to create a text-based visualization.
    Automatically handles circuits with different signatures by providing
    dummy parameter values when needed.

    Args:
        circuit_repr: The circuit representation to visualize.

    Returns:
        ASCII diagram as a string that can be printed to the terminal.

    Raises:
        ValueError: If the circuit representation has no QNode set.

    Example:
        >>> from skadi.core.circuit_generator import CircuitGenerator
        >>> generator = CircuitGenerator()
        >>> circuit = generator.generate_circuit("Create a Bell state")
        >>> diagram = visualize_circuit(circuit)
        >>> print(diagram)
    """
    if circuit_repr.qnode is None:
        raise ValueError("Cannot visualize circuit: QNode is not set")

    # Inspect the circuit function signature to determine parameters
    sig = inspect.signature(circuit_repr.qnode.func)
    params = list(sig.parameters.values())

    # Create drawer with clean output options
    drawer = qml.draw(circuit_repr.qnode, decimals=2, show_all_wires=True)

    # Call drawer with appropriate arguments
    if not params:
        # No parameters - call without arguments
        return drawer()

    # Has parameters - prepare dummy arguments
    dummy_args = []
    for param in params:
        # Use annotation if available, otherwise default to float
        param_type = (
            param.annotation if param.annotation != inspect.Parameter.empty else float
        )

        # Generate appropriate dummy value based on type
        if param_type in (int, float) or param_type is inspect.Parameter.empty:
            dummy_args.append(0.0)
        elif param_type is list:
            dummy_args.append([0.0])
        else:
            # For other types, try 0.0 as a reasonable default
            dummy_args.append(0.0)

    return drawer(*dummy_args)
