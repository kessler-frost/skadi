"""Circuit analysis and explanation generation."""

from typing import Any, Dict, Optional


from skadi.core.circuit_representation import CircuitRepresentation
from skadi.engine.llm_client import LLMClient


class CircuitAnalyzer:
    """Analyze quantum circuits and generate explanations.

    This class provides comprehensive circuit analysis including resource
    estimation, structural analysis, and LLM-powered natural language
    explanations of circuit behavior.

    Features:
        - Resource estimation (gates, depth, wires)
        - Circuit visualization
        - Complexity assessment
        - Natural language explanation generation
        - Gate type analysis

    Example:
        >>> analyzer = CircuitAnalyzer(llm_client)
        >>> analysis = analyzer.analyze(circuit, include_explanation=True)
        >>> print(analysis["explanation"])
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize the circuit analyzer.

        Args:
            llm_client: LLM client for generating explanations (optional)

        """
        self.llm_client = llm_client

    def analyze(
        self,
        circuit: CircuitRepresentation,
        include_explanation: bool = True,
        include_visualization: bool = True,
    ) -> Dict[str, Any]:
        """Generate comprehensive circuit analysis.

        Args:
            circuit: CircuitRepresentation to analyze
            include_explanation: Generate LLM-powered explanation
            include_visualization: Include circuit diagram

        Returns:
            Dictionary containing analysis results

        Raises:
            ValueError: If circuit has no qnode

        Example:
            >>> analyzer = CircuitAnalyzer(llm_client)
            >>> analysis = analyzer.analyze(circuit)
            >>> print(analysis["specs"])
            >>> print(analysis["explanation"])
        """
        if circuit.qnode is None:
            raise ValueError("Circuit must have a qnode to analyze")

        analysis = {
            "description": circuit.description,
            "specs": self._get_detailed_specs(circuit),
            "resources": circuit.get_resource_summary(),
            "complexity": self._assess_complexity(circuit),
        }

        if include_visualization:
            analysis["visualization"] = circuit.get_visualization()

        if include_explanation and self.llm_client:
            analysis["explanation"] = self._generate_explanation(circuit, analysis)

        return analysis

    def _get_detailed_specs(self, circuit: CircuitRepresentation) -> Dict[str, Any]:
        """Get detailed circuit specifications.

        Args:
            circuit: CircuitRepresentation to analyze

        Returns:
            Dictionary with detailed specs
        """
        specs = circuit.get_specs()

        # Extract from resources object
        resources = specs["resources"]

        return {
            "num_operations": resources.num_gates,
            "depth": resources.depth,
            "num_wires": specs["num_device_wires"],
            "num_used_wires": specs["num_tape_wires"],
            "num_trainable_params": specs["num_trainable_params"],
            "gate_types": dict(resources.gate_types),
            "gate_sizes": dict(resources.gate_sizes),
            "diff_method": specs["diff_method"],
        }

    def _assess_complexity(self, circuit: CircuitRepresentation) -> Dict[str, Any]:
        """Assess circuit complexity.

        Args:
            circuit: CircuitRepresentation to assess

        Returns:
            Dictionary with complexity metrics
        """
        specs = circuit.get_specs()
        resources = specs["resources"]

        num_ops = resources.num_gates
        depth = resources.depth
        num_wires = specs["num_device_wires"]

        # Simple complexity categorization
        if num_ops <= 5 and depth <= 5:
            complexity_level = "simple"
        elif num_ops <= 20 and depth <= 10:
            complexity_level = "moderate"
        else:
            complexity_level = "complex"

        # Count entangling gates (multi-qubit gates)
        gate_sizes = dict(resources.gate_sizes)
        entangling_gates = sum(count for size, count in gate_sizes.items() if size > 1)

        return {
            "level": complexity_level,
            "total_operations": num_ops,
            "circuit_depth": depth,
            "entangling_gates": entangling_gates,
            "qubit_count": num_wires,
            "operations_per_qubit": num_ops / num_wires if num_wires > 0 else 0,
        }

    def _generate_explanation(
        self, circuit: CircuitRepresentation, analysis: Dict[str, Any]
    ) -> str:
        """Generate natural language explanation using LLM.

        Args:
            circuit: CircuitRepresentation to explain
            analysis: Analysis results

        Returns:
            Natural language explanation
        """
        # Build context from circuit information
        specs = analysis["specs"]
        complexity = analysis["complexity"]
        visualization = analysis.get("visualization", "")

        # Create analysis prompt
        prompt = f"""Analyze and explain this quantum circuit in clear, concise language.

Circuit Information:
- Description: {circuit.description or "Not provided"}
- Total operations: {specs["num_operations"]}
- Circuit depth: {specs["depth"]}
- Qubits: {specs["num_wires"]}
- Gate types: {specs["gate_types"]}
- Complexity level: {complexity["level"]}
- Entangling gates: {complexity["entangling_gates"]}

Circuit Diagram:
{visualization}

Code:
{circuit.code or "Not available"}

Please provide:
1. What quantum algorithm or pattern this circuit implements
2. Key operations and their purpose
3. Expected behavior and use cases
4. Any notable characteristics or optimizations

Keep the explanation concise and suitable for someone familiar with quantum computing basics."""

        # Generate explanation
        explanation = self.llm_client.generate_circuit_code(prompt)

        return explanation

    def compare_circuits(
        self,
        circuit1: CircuitRepresentation,
        circuit2: CircuitRepresentation,
        names: Optional[tuple[str, str]] = None,
    ) -> Dict[str, Any]:
        """Compare two circuits side by side.

        Args:
            circuit1: First circuit to compare
            circuit2: Second circuit to compare
            names: Optional names for the circuits (default: "Circuit 1", "Circuit 2")

        Returns:
            Dictionary with comparison results

        Example:
            >>> analyzer = CircuitAnalyzer()
            >>> comparison = analyzer.compare_circuits(original, optimized)
            >>> print(comparison["differences"])
        """
        if names is None:
            names = ("Circuit 1", "Circuit 2")

        specs1 = circuit1.get_specs()
        specs2 = circuit2.get_specs()

        resources1 = specs1["resources"]
        resources2 = specs2["resources"]

        comparison = {
            "circuits": names,
            "circuit1": {
                "operations": resources1.num_gates,
                "depth": resources1.depth,
                "wires": specs1["num_device_wires"],
                "gate_types": dict(resources1.gate_types),
            },
            "circuit2": {
                "operations": resources2.num_gates,
                "depth": resources2.depth,
                "wires": specs2["num_device_wires"],
                "gate_types": dict(resources2.gate_types),
            },
            "differences": {
                "operations": resources2.num_gates - resources1.num_gates,
                "depth": resources2.depth - resources1.depth,
                "wires": specs2["num_device_wires"] - specs1["num_device_wires"],
            },
        }

        return comparison

    def get_gate_analysis(self, circuit: CircuitRepresentation) -> Dict[str, Any]:
        """Analyze gate usage in the circuit.

        Args:
            circuit: CircuitRepresentation to analyze

        Returns:
            Dictionary with gate analysis

        Example:
            >>> analyzer = CircuitAnalyzer()
            >>> gate_info = analyzer.get_gate_analysis(circuit)
            >>> print(gate_info["single_qubit_gates"])
        """
        specs = circuit.get_specs()
        resources = specs["resources"]
        gate_types = dict(resources.gate_types)
        gate_sizes = dict(resources.gate_sizes)

        # Categorize gates by type
        single_qubit_gates = {}
        multi_qubit_gates = {}

        for gate_name, count in gate_types.items():
            # Determine if single or multi-qubit (heuristic based on name)
            if any(
                multi in gate_name.lower()
                for multi in ["cnot", "cx", "cz", "swap", "toffoli", "controlled"]
            ):
                multi_qubit_gates[gate_name] = count
            else:
                single_qubit_gates[gate_name] = count

        return {
            "total_gates": resources.num_gates,
            "gate_types": gate_types,
            "gate_sizes": gate_sizes,
            "single_qubit_gates": single_qubit_gates,
            "multi_qubit_gates": multi_qubit_gates,
            "single_qubit_count": sum(single_qubit_gates.values()),
            "multi_qubit_count": sum(multi_qubit_gates.values()),
        }
