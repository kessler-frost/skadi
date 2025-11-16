"""Main circuit generator that converts natural language to PennyLane circuits."""

from typing import Any, Callable, Dict, Optional

import pennylane as qml

from skadi.engine.llm_client import LLMClient


class CircuitGenerator:
    """Generate PennyLane quantum circuits from natural language descriptions."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "anthropic/claude-3.5-haiku"
    ):
        """
        Initialize the circuit generator.

        Args:
            api_key: OpenRouter API key. If None, will use OPENROUTER_API_KEY from environment.
            model: The model to use for generation. Defaults to Claude 3.5 Haiku.
        """
        self.llm_client = LLMClient(api_key=api_key, model=model)

    def generate(self, description: str) -> Callable:
        """
        Generate a PennyLane circuit from natural language description.

        Args:
            description: Natural language description of the quantum circuit.

        Returns:
            A PennyLane QNode function representing the circuit.

        Raises:
            ValueError: If the generated code is invalid or cannot be executed.
            Exception: If circuit generation fails.
        """
        # Generate the circuit code using LLM
        code = self.llm_client.generate_circuit_code(description)

        # Validate the generated code
        self._validate_code(code)

        # Execute the code to create the circuit function
        circuit = self._execute_code(code)

        return circuit

    def _validate_code(self, code: str) -> None:
        """
        Validate that the generated code contains required PennyLane components.

        Args:
            code: The generated Python code string.

        Raises:
            ValueError: If the code is invalid or missing required components.
        """
        if not code or len(code.strip()) == 0:
            raise ValueError("Generated code is empty")

        # Check for required imports
        if "import pennylane" not in code and "from pennylane" not in code:
            raise ValueError("Generated code must import pennylane")

        # Check for device creation
        if "qml.device" not in code:
            raise ValueError("Generated code must create a quantum device")

        # Check for circuit function definition
        if "def circuit" not in code:
            raise ValueError("Generated code must define a 'circuit' function")

        # Check for QNode decorator
        if "@qml.qnode" not in code:
            raise ValueError("Generated code must use @qml.qnode decorator")

        # Check for return statement
        if "return" not in code:
            raise ValueError("Circuit function must have a return statement")

    def _execute_code(self, code: str) -> Callable:
        """
        Execute the generated code and extract the circuit function.

        Args:
            code: The generated Python code string.

        Returns:
            The circuit function from the executed code.

        Raises:
            ValueError: If the code cannot be executed or circuit function not found.
        """
        # Create a namespace for execution
        namespace: Dict[str, Any] = {
            "qml": qml,
            "pennylane": qml,
        }

        try:
            # Execute the generated code
            exec(code, namespace)

            # Extract the circuit function
            if "circuit" not in namespace:
                raise ValueError(
                    "Circuit function 'circuit' not found in generated code"
                )

            circuit = namespace["circuit"]

            # Verify it's callable
            if not callable(circuit):
                raise ValueError("'circuit' is not a callable function")

            return circuit

        except SyntaxError as e:
            raise ValueError(f"Syntax error in generated code: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error executing generated code: {str(e)}")

    def generate_with_code(self, description: str) -> tuple[Callable, str]:
        """
        Generate a circuit and also return the generated code.

        Args:
            description: Natural language description of the quantum circuit.

        Returns:
            A tuple of (circuit_function, generated_code).

        Raises:
            ValueError: If the generated code is invalid or cannot be executed.
            Exception: If circuit generation fails.
        """
        code = self.llm_client.generate_circuit_code(description)
        self._validate_code(code)
        circuit = self._execute_code(code)
        return circuit, code
