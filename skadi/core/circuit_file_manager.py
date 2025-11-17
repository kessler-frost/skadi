"""Circuit file manager for saving and loading quantum circuits."""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pennylane as qml

from skadi.core.circuit_representation import CircuitRepresentation


def save_circuit(
    circuit_repr: CircuitRepresentation, filename: str = "circuit.py"
) -> Path:
    """Save a circuit representation to a Python file.

    Args:
        circuit_repr: CircuitRepresentation object containing the circuit code
        filename: Name of file to save to (default: "circuit.py")

    Returns:
        Path object of the saved file

    Raises:
        ValueError: If circuit_repr.code is None or empty
    """
    if not circuit_repr.code:
        raise ValueError("CircuitRepresentation has no code to save")

    file_path = Path.cwd() / filename

    # Write code to file
    file_path.write_text(circuit_repr.code)

    return file_path


def load_circuit(filename: str = "circuit.py") -> Optional[CircuitRepresentation]:
    """Load a circuit from a Python file.

    Executes the circuit code to extract the circuit function and wraps it
    in a CircuitRepresentation object.

    Args:
        filename: Name of file to load from (default: "circuit.py")

    Returns:
        CircuitRepresentation object with the loaded circuit, or None if file doesn't exist

    Raises:
        ValueError: If the loaded code is invalid or cannot be executed
    """
    file_path = Path.cwd() / filename

    if not file_path.exists():
        return None

    # Read code from file
    code = file_path.read_text()

    # Execute code to extract circuit function (similar to CircuitGenerator._execute_code)
    circuit = _execute_code(code)

    # Create CircuitRepresentation with the loaded circuit
    return CircuitRepresentation(
        qnode=circuit,
        code=code,
        description=f"Loaded from {filename}",
        metadata={"source_file": str(file_path)},
    )


def circuit_exists(filename: str = "circuit.py") -> bool:
    """Check if a circuit file exists in the current directory.

    Args:
        filename: Name of file to check (default: "circuit.py")

    Returns:
        True if file exists, False otherwise
    """
    file_path = Path.cwd() / filename
    return file_path.exists()


def _execute_code(code: str) -> Callable:
    """Execute circuit code and extract the circuit function.

    This is an internal helper function that mimics CircuitGenerator._execute_code.

    Args:
        code: Python code string containing circuit definition

    Returns:
        The executable circuit function (QNode)

    Raises:
        ValueError: If code cannot be executed or circuit function not found
    """
    # Create namespace for execution with PennyLane available
    namespace: Dict[str, Any] = {
        "qml": qml,
        "pennylane": qml,
    }

    try:
        # Execute the code
        exec(code, namespace)

        # Extract the circuit function
        if "circuit" not in namespace:
            raise ValueError("Circuit function 'circuit' not found in loaded code")

        circuit = namespace["circuit"]

        # Verify it's callable
        if not callable(circuit):
            raise ValueError("'circuit' is not a callable function")

        return circuit

    except SyntaxError as e:
        raise ValueError(f"Syntax error in loaded code: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error executing loaded code: {str(e)}")
