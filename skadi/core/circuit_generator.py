"""Main circuit generator that converts natural language to PennyLane circuits."""

import re
from typing import Any, Callable, Dict, Optional

import pennylane as qml

from skadi.config import settings
from skadi.core.circuit_representation import CircuitRepresentation
from skadi.engine.llm_client import LLMClient
from skadi.knowledge.augmenter import KnowledgeAugmenter


class CircuitGenerator:
    """
    Generate PennyLane quantum circuits from natural language descriptions.

    Enhanced with dual knowledge system:
    - PennyLaneKnowledge: Conceptual understanding of quantum algorithms and patterns
    - Context7Client: API-specific documentation and code examples
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_knowledge: Optional[bool] = None,
        use_pennylane_kb: Optional[bool] = None,
        use_context7: Optional[bool] = None,
        max_retries: int = 3,
    ):
        """
        Initialize the circuit generator.

        Args:
            api_key: LLM API key. If None, uses settings.skadi_api_key.
            model: The model to use for generation. If None, uses settings.skadi_model.
            use_knowledge: Whether to use knowledge augmentation. If None, uses settings.use_knowledge.
            use_pennylane_kb: Whether to use PennyLane knowledge base. If None, uses settings.use_pennylane_kb.
            use_context7: Whether to use Context7 API docs. If None, uses settings.use_context7.
            max_retries: Maximum number of retries on syntax/compilation errors (default: 3).
        """
        # Use settings as defaults, allow constructor overrides
        self.llm_client = LLMClient(
            api_key=api_key,
            model=model or settings.skadi_model,
        )
        self.use_knowledge = (
            use_knowledge if use_knowledge is not None else settings.use_knowledge
        )
        self.max_retries = max_retries

        # Initialize knowledge augmenter if enabled
        if self.use_knowledge:
            self.knowledge_augmenter = KnowledgeAugmenter(
                use_pennylane_kb=use_pennylane_kb
                if use_pennylane_kb is not None
                else settings.use_pennylane_kb,
                use_context7=use_context7
                if use_context7 is not None
                else settings.use_context7,
            )
        else:
            self.knowledge_augmenter = None

    def _generate_internal(
        self, description: str, use_knowledge: Optional[bool] = None
    ) -> tuple[Callable, str]:
        """Internal method that all generation methods call.

        Args:
            description: Natural language description of the quantum circuit.
            use_knowledge: Override to enable/disable knowledge augmentation.

        Returns:
            Tuple of (circuit_function, generated_code).

        Raises:
            ValueError: If code generation fails after all retries.
        """
        should_use_knowledge = (
            use_knowledge if use_knowledge is not None else self.use_knowledge
        )

        knowledge_context = ""
        if should_use_knowledge and self.knowledge_augmenter:
            knowledge_context = self._retrieve_knowledge(description)

        error_feedback = ""
        last_error = None

        for attempt in range(self.max_retries):
            code = self.llm_client.generate_circuit_code(
                description, knowledge_context, error_feedback
            )

            # Try to validate and execute the code
            validation_error = self._try_validate_code(code)
            if validation_error:
                error_feedback = f"Validation error: {validation_error}"
                last_error = ValueError(error_feedback)
                continue

            circuit, execution_error = self._try_execute_code(code)
            if execution_error:
                error_feedback = f"Execution error: {execution_error}"
                last_error = ValueError(error_feedback)
                continue

            # Try to compile/draw the circuit to catch compilation errors
            compilation_error = self._try_compile_circuit(circuit)
            if compilation_error:
                error_feedback = f"Compilation error: {compilation_error}"
                last_error = ValueError(error_feedback)
                continue

            # Success - all checks passed
            return circuit, code

        # All retries exhausted
        raise last_error or ValueError(
            f"Failed to generate valid circuit after {self.max_retries} attempts"
        )

    def generate(
        self, description: str, use_knowledge: Optional[bool] = None
    ) -> Callable:
        """
        Generate a PennyLane circuit from natural language description.

        Uses dual knowledge system to enhance generation:
        1. PennyLaneKnowledge: Provides conceptual understanding of quantum patterns
        2. Context7Client: Provides API-specific syntax and examples

        Args:
            description: Natural language description of the quantum circuit.
            use_knowledge: Override to enable/disable knowledge augmentation for this call.
                         If None, uses instance setting.

        Returns:
            A PennyLane QNode function representing the circuit.

        Raises:
            ValueError: If the generated code is invalid or cannot be executed.
            Exception: If circuit generation fails.
        """
        circuit, _ = self._generate_internal(description, use_knowledge)
        return circuit

    def _retrieve_knowledge(self, description: str) -> str:
        """
        Retrieve and combine knowledge from all sources.

        Args:
            description: Circuit description query.

        Returns:
            Combined knowledge context string.
        """
        if not self.knowledge_augmenter:
            return ""

        # Use augmenter to get combined context from both sources
        base_prompt = """You are an expert quantum computing assistant specialized in PennyLane.
Generate valid PennyLane circuit code from this description: {description}"""

        # This will query both PennyLane KB and Context7, combine them, and format
        enhanced_prompt = self.knowledge_augmenter.augment_prompt(
            user_query=description,
            base_prompt=base_prompt,
            max_knowledge_tokens=settings.max_knowledge_tokens,
        )

        # Extract just the knowledge context portion
        # (The augmenter includes it in the full prompt, but we want just the context)
        if "KNOWLEDGE CONTEXT:" in enhanced_prompt:
            parts = enhanced_prompt.split("KNOWLEDGE CONTEXT:")
            if len(parts) > 1:
                context_section = parts[1].split("---")[0].strip()
                return context_section

        return ""

    def _try_validate_code(self, code: str) -> Optional[str]:
        """
        Validate that the generated code contains required PennyLane components.

        Args:
            code: The generated Python code string.

        Returns:
            Error message if validation fails, None if validation passes.
        """
        validations = {
            r"\S": "Generated code is empty",
            r"(?:import|from)\s+pennylane": "Generated code must import pennylane",
            r"qml\.device": "Generated code must create a quantum device",
            r"def\s+circuit": "Generated code must define a 'circuit' function",
            r"@qml\.qnode": "Generated code must use @qml.qnode decorator",
            r"\breturn\b": "Circuit function must have a return statement",
        }

        for pattern, error_msg in validations.items():
            if not re.search(pattern, code):
                return error_msg

        return None

    def _try_execute_code(self, code: str) -> tuple[Optional[Callable], Optional[str]]:
        """
        Execute the generated code and extract the circuit function.

        Args:
            code: The generated Python code string.

        Returns:
            Tuple of (circuit_function, error_message).
            Returns (circuit, None) on success, (None, error_msg) on failure.
        """
        namespace: Dict[str, Any] = {
            "qml": qml,
            "pennylane": qml,
        }

        try:
            # Execute the generated code
            exec(code, namespace)
        except SyntaxError as e:
            return None, f"Syntax error: {e.msg} at line {e.lineno}"
        except Exception as e:
            return None, f"Execution error: {type(e).__name__}: {str(e)}"

        # Extract the circuit function
        if "circuit" not in namespace:
            return None, "Circuit function 'circuit' not found in generated code"

        circuit = namespace["circuit"]

        # Verify it's callable
        if not callable(circuit):
            return None, "'circuit' is not a callable function"

        return circuit, None

    def _try_compile_circuit(self, circuit: Callable) -> Optional[str]:
        """
        Try to compile the circuit to catch compilation errors without execution.

        Args:
            circuit: The circuit function to test.

        Returns:
            Error message if compilation fails, None if successful.
        """
        try:
            # Use qml.specs to compile/analyze the circuit without executing it
            # This will construct the quantum tape and validate the circuit structure
            qml.specs(circuit)()
            return None
        except Exception as e:
            return f"Compilation error: {type(e).__name__}: {str(e)}"

    def generate_with_code(
        self, description: str, use_knowledge: Optional[bool] = None
    ) -> tuple[Callable, str]:
        """
        Generate a circuit and also return the generated code.

        Args:
            description: Natural language description of the quantum circuit.
            use_knowledge: Override to enable/disable knowledge augmentation for this call.
                         If None, uses instance setting.

        Returns:
            A tuple of (circuit_function, generated_code).

        Raises:
            ValueError: If the generated code is invalid or cannot be executed.
            Exception: If circuit generation fails.
        """
        return self._generate_internal(description, use_knowledge)

    def get_knowledge_stats(self, query: str) -> Dict[str, Any]:
        """
        Get statistics about knowledge retrieval for a query.

        Useful for debugging and understanding what knowledge is being used.

        Args:
            query: Circuit description query.

        Returns:
            Dictionary with retrieval statistics, or empty dict if knowledge disabled.
        """
        if not self.knowledge_augmenter:
            return {"knowledge_enabled": False}

        stats = self.knowledge_augmenter.get_retrieval_stats(query)
        stats["knowledge_enabled"] = True
        return stats

    def generate_circuit(
        self, description: str, use_knowledge: Optional[bool] = None
    ) -> CircuitRepresentation:
        """
        Generate a circuit and return it as a CircuitRepresentation object.

        This method provides the full circuit representation with metadata,
        code, and transformation tracking capabilities.

        Args:
            description: Natural language description of the quantum circuit.
            use_knowledge: Override to enable/disable knowledge augmentation for this call.
                         If None, uses instance setting.

        Returns:
            CircuitRepresentation object with qnode, code, and metadata.

        Raises:
            ValueError: If the generated code is invalid or cannot be executed.
            Exception: If circuit generation fails.

        Example:
            >>> generator = CircuitGenerator()
            >>> circuit = generator.generate_circuit("Create a Bell state")
            >>> print(circuit.get_specs())
            >>> print(circuit.get_visualization())
        """
        qnode, code = self._generate_internal(description, use_knowledge)
        should_use_knowledge = (
            use_knowledge if use_knowledge is not None else self.use_knowledge
        )

        return CircuitRepresentation(
            qnode=qnode,
            code=code,
            description=description,
            metadata={
                "model": self.llm_client.model_id,
                "use_knowledge": should_use_knowledge,
                "use_pennylane_kb": (
                    self.knowledge_augmenter.use_pennylane_kb
                    if self.knowledge_augmenter
                    else False
                ),
                "use_context7": (
                    self.knowledge_augmenter.use_context7
                    if self.knowledge_augmenter
                    else False
                ),
            },
        )
