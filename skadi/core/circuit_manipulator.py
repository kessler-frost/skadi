"""Unified interface for circuit manipulation operations."""

from typing import Any, Dict, Optional

from skadi.config import settings
from skadi.core.circuit_representation import CircuitRepresentation
from skadi.engine.llm_client import LLMClient
from skadi.knowledge.augmenter import KnowledgeAugmenter
from skadi.manipulation.analyzer import CircuitAnalyzer
from skadi.manipulation.optimizer import CircuitOptimizer
from skadi.manipulation.rewriter import CircuitRewriter
from skadi.manipulation.transformer import CircuitTransformer


class CircuitManipulator:
    """Unified interface for quantum circuit manipulation.

    This class provides a comprehensive API for manipulating quantum circuits,
    including transformation, optimization, analysis, and rewriting operations.

    Features:
        - Apply PennyLane transforms
        - Optimize circuits for depth and gate count
        - Analyze and explain circuits
        - Rewrite circuits using natural language

    Example:
        >>> from skadi import CircuitGenerator, CircuitManipulator
        >>> generator = CircuitGenerator()
        >>> circuit = generator.generate_circuit("Create a Bell state")
        >>>
        >>> manipulator = CircuitManipulator()
        >>> optimized = manipulator.optimize(circuit, level="aggressive")
        >>> analysis = manipulator.understand(circuit)
        >>> modified = manipulator.rewrite(circuit, "Add a phase gate")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_knowledge: bool = True,
    ):
        """Initialize the circuit manipulator.

        Args:
            api_key: LLM API key (for LLM-based operations). If None, uses settings.
            model: Model to use. If None, uses settings.
            use_knowledge: Enable knowledge augmentation for LLM operations
        """
        # Initialize LLM client for rewriting and analysis
        self.llm_client = LLMClient(
            api_key=api_key or settings.skadi_api_key,
            model=model or settings.skadi_model,
        )

        # Initialize knowledge augmenter if enabled
        self.knowledge_augmenter = None
        if use_knowledge:
            self.knowledge_augmenter = KnowledgeAugmenter(
                use_pennylane_kb=settings.use_pennylane_kb,
                use_context7=settings.use_context7,
            )

        # Initialize manipulation components
        self.transformer = CircuitTransformer()
        self.optimizer = CircuitOptimizer()
        self.analyzer = CircuitAnalyzer(self.llm_client, self.knowledge_augmenter)
        self.rewriter = CircuitRewriter(self.llm_client, self.knowledge_augmenter)

    def optimize(
        self,
        circuit: CircuitRepresentation,
        level: str = "default",
        num_passes: int = 1,
        **kwargs: Any,
    ) -> CircuitRepresentation:
        """Optimize a circuit.

        Args:
            circuit: Circuit to optimize
            level: Optimization level ("basic", "default", "aggressive")
            num_passes: Number of optimization passes
            **kwargs: Additional optimization parameters

        Returns:
            Optimized circuit with improvement stats

        Example:
            >>> manipulator = CircuitManipulator()
            >>> optimized = manipulator.optimize(circuit, level="aggressive", num_passes=3)
            >>> print(optimized.transform_history[-1]["improvement"])
        """
        return self.optimizer.optimize(
            circuit, level=level, num_passes=num_passes, **kwargs
        )

    def understand(
        self,
        circuit: CircuitRepresentation,
        include_explanation: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Analyze and explain a circuit.

        Args:
            circuit: Circuit to analyze
            include_explanation: Generate LLM-powered explanation
            verbose: Include detailed analysis

        Returns:
            Analysis dictionary with specs, resources, and explanation

        Example:
            >>> manipulator = CircuitManipulator()
            >>> analysis = manipulator.understand(circuit)
            >>> print(analysis["explanation"])
            >>> print(analysis["specs"])
        """
        analysis = self.analyzer.analyze(
            circuit,
            include_explanation=include_explanation,
            include_visualization=verbose,
        )

        if verbose:
            # Add gate analysis in verbose mode
            analysis["gate_analysis"] = self.analyzer.get_gate_analysis(circuit)

        return analysis

    def rewrite(
        self,
        circuit: CircuitRepresentation,
        modification_request: str,
        use_knowledge: bool = True,
    ) -> CircuitRepresentation:
        """Rewrite a circuit based on natural language request.

        Args:
            circuit: Circuit to modify
            modification_request: Natural language description of changes
            use_knowledge: Use knowledge augmentation

        Returns:
            Modified circuit

        Example:
            >>> manipulator = CircuitManipulator()
            >>> modified = manipulator.rewrite(
            ...     circuit,
            ...     "Add a rotation before the CNOT gate"
            ... )
        """
        return self.rewriter.rewrite(
            circuit,
            modification_request,
            use_knowledge=use_knowledge,
        )

    def compare_circuits(
        self,
        circuit1: CircuitRepresentation,
        circuit2: CircuitRepresentation,
        names: Optional[tuple[str, str]] = None,
    ) -> Dict[str, Any]:
        """Compare two circuits.

        Args:
            circuit1: First circuit
            circuit2: Second circuit
            names: Optional names for the circuits

        Returns:
            Comparison dictionary

        Example:
            >>> original = generator.generate_circuit("Bell state")
            >>> optimized = manipulator.optimize(original)
            >>> comparison = manipulator.compare_circuits(original, optimized)
        """
        return self.analyzer.compare_circuits(circuit1, circuit2, names)

    def get_optimization_report(self, circuit: CircuitRepresentation) -> Dict[str, Any]:
        """Get optimization report for a circuit.

        Args:
            circuit: Circuit with optimization history

        Returns:
            Optimization report

        Example:
            >>> optimized = manipulator.optimize(circuit)
            >>> report = manipulator.get_optimization_report(optimized)
        """
        return self.optimizer.get_optimization_report(circuit)
