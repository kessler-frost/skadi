"""LLM-guided circuit rewriting and modification."""

from typing import Any, Dict, Optional

from skadi.core.circuit_representation import CircuitRepresentation
from skadi.engine.llm_client import LLMClient
from skadi.knowledge.augmenter import KnowledgeAugmenter


class CircuitRewriter:
    """Rewrite and modify circuits using natural language requests.

    This class uses an LLM to understand modification requests and generate
    modified circuit code. It preserves circuit metadata and tracks the
    modifications in the transformation history.

    Example:
        >>> rewriter = CircuitRewriter(llm_client, knowledge_augmenter)
        >>> modified = rewriter.rewrite(
        ...     circuit,
        ...     "Add a rotation before measurement"
        ... )
        >>> print(modified.code)
    """

    def __init__(
        self,
        llm_client: LLMClient,
        knowledge_augmenter: Optional[KnowledgeAugmenter] = None,
    ):
        """Initialize the circuit rewriter.

        Args:
            llm_client: LLM client for code generation
            knowledge_augmenter: Knowledge augmenter for context (optional)
        """
        self.llm_client = llm_client
        self.knowledge_augmenter = knowledge_augmenter

    def rewrite(
        self,
        circuit: CircuitRepresentation,
        modification_request: str,
        use_knowledge: bool = True,
        preserve_structure: bool = True,
    ) -> CircuitRepresentation:
        """Rewrite a circuit based on natural language modification request.

        Args:
            circuit: CircuitRepresentation to modify
            modification_request: Natural language description of changes
            use_knowledge: Use knowledge augmentation for better results
            preserve_structure: Try to preserve overall circuit structure

        Returns:
            New CircuitRepresentation with modifications applied

        Raises:
            ValueError: If circuit has no code or modification fails

        Example:
            >>> rewriter = CircuitRewriter(llm_client)
            >>> modified = rewriter.rewrite(
            ...     circuit,
            ...     "Replace all Hadamard gates with X gates"
            ... )
        """
        if circuit.code is None:
            raise ValueError("Circuit must have code to rewrite")

        # Get current circuit information
        before_specs = circuit.get_specs() if circuit.qnode else None
        visualization = circuit.get_visualization() if circuit.qnode else ""

        # Build rewrite prompt
        prompt = self._build_rewrite_prompt(
            circuit, modification_request, visualization, preserve_structure
        )

        # Augment with knowledge if requested
        if use_knowledge and self.knowledge_augmenter:
            base_prompt = (
                "Modify quantum circuit based on user request. "
                "Ensure the code is valid PennyLane code."
            )
            prompt = (
                self.knowledge_augmenter.augment_prompt(
                    modification_request, base_prompt
                )
                + "\n\n"
                + prompt
            )

        # Generate modified code
        modified_code = self.llm_client.generate_circuit_code(prompt)

        # Validate and execute the modified code
        from skadi.core.circuit_generator import CircuitGenerator

        # Create a temporary generator to validate/execute the code
        temp_generator = CircuitGenerator(
            api_key=self.llm_client.api_key,
            model=self.llm_client.model_id,
            use_knowledge=False,  # Don't use knowledge for validation
        )

        # Validate the code
        validation_error = temp_generator._try_validate_code(modified_code)
        if validation_error:
            raise ValueError(f"Code validation failed: {validation_error}")

        # Execute to get the qnode
        modified_qnode, execution_error = temp_generator._try_execute_code(modified_code)
        if execution_error:
            raise ValueError(f"Code execution failed: {execution_error}")

        # Try to compile the circuit
        compilation_error = temp_generator._try_compile_circuit(modified_qnode)
        if compilation_error:
            raise ValueError(f"Circuit compilation failed: {compilation_error}")

        # Create new circuit representation
        new_circuit = CircuitRepresentation(
            qnode=modified_qnode,
            code=modified_code,
            description=f"{circuit.description or 'Original circuit'} - {modification_request}",
            metadata=circuit.metadata.copy(),
        )

        # Copy transform history
        new_circuit.transform_history = circuit.transform_history.copy()

        # Get specs after modification
        after_specs = new_circuit.get_specs()

        # Record modification in history
        new_circuit.add_transform(
            transform_name="rewrite",
            transform_params={
                "modification_request": modification_request,
                "use_knowledge": use_knowledge,
                "preserve_structure": preserve_structure,
            },
            before_specs=before_specs,
            after_specs=after_specs,
        )

        return new_circuit

    def _build_rewrite_prompt(
        self,
        circuit: CircuitRepresentation,
        modification_request: str,
        visualization: str,
        preserve_structure: bool,
    ) -> str:
        """Build the prompt for circuit rewriting.

        Args:
            circuit: Original circuit
            modification_request: User's modification request
            visualization: Circuit diagram
            preserve_structure: Whether to preserve structure

        Returns:
            Formatted prompt for LLM
        """
        structure_instruction = (
            "Preserve the overall structure and intent of the original circuit "
            "while making the requested modifications."
            if preserve_structure
            else "Make the requested modifications. You can restructure the circuit as needed."
        )

        prompt = f"""You are modifying an existing PennyLane quantum circuit.

Original Circuit Description: {circuit.description or "Not provided"}

Current Circuit Code:
```python
{circuit.code}
```

Current Circuit Diagram:
{visualization}

Modification Request: {modification_request}

Instructions:
1. {structure_instruction}
2. Ensure the modified code is valid PennyLane code
3. Include all necessary imports
4. Define the device and use @qml.qnode decorator
5. Maintain a function named 'circuit'
6. Add comments explaining the modifications

Generate the complete modified circuit code below:"""

        return prompt

    def modify_operations(
        self,
        circuit: CircuitRepresentation,
        operation_changes: Dict[str, Any],
    ) -> CircuitRepresentation:
        """Modify specific operations in the circuit.

        Args:
            circuit: CircuitRepresentation to modify
            operation_changes: Dictionary describing operation changes

        Returns:
            Modified CircuitRepresentation

        Example:
            >>> rewriter = CircuitRewriter(llm_client)
            >>> changes = {
            ...     "replace": {"Hadamard": "X"},
            ...     "remove": ["PauliZ"],
            ...     "add_before_measurement": "RZ(0.5, wires=0)"
            ... }
            >>> modified = rewriter.modify_operations(circuit, changes)
        """
        # Build modification request from operation changes
        modifications = []

        if "replace" in operation_changes:
            for old_op, new_op in operation_changes["replace"].items():
                modifications.append(f"Replace all {old_op} gates with {new_op}")

        if "remove" in operation_changes:
            for op in operation_changes["remove"]:
                modifications.append(f"Remove all {op} gates")

        if "add_before_measurement" in operation_changes:
            op = operation_changes["add_before_measurement"]
            modifications.append(f"Add {op} before measurement")

        if "add_after_initialization" in operation_changes:
            op = operation_changes["add_after_initialization"]
            modifications.append(f"Add {op} at the beginning of the circuit")

        modification_request = ". ".join(modifications)

        return self.rewrite(circuit, modification_request)

    def explain_and_simplify(
        self, circuit: CircuitRepresentation
    ) -> CircuitRepresentation:
        """Simplify circuit while maintaining functionality.

        This method asks the LLM to analyze the circuit and simplify it
        by removing redundant operations or replacing complex sequences
        with simpler equivalents.

        Args:
            circuit: CircuitRepresentation to simplify

        Returns:
            Simplified CircuitRepresentation

        Example:
            >>> rewriter = CircuitRewriter(llm_client)
            >>> simplified = rewriter.explain_and_simplify(circuit)
        """
        modification_request = (
            "Simplify this circuit by removing redundant operations and "
            "replacing complex gate sequences with simpler equivalents. "
            "Maintain the same quantum functionality."
        )

        return self.rewrite(circuit, modification_request, preserve_structure=False)
