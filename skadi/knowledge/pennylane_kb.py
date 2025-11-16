"""PennyLane knowledge base for quantum computing concepts and algorithms."""

from typing import Any, Dict, List, Optional


class PennyLaneKnowledge:
    """
    Knowledge base for PennyLane quantum computing concepts.

    Provides conceptual understanding of quantum algorithms, patterns,
    and theoretical foundations to augment circuit generation.
    """

    def __init__(self):
        """Initialize the PennyLane knowledge base."""
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base with quantum computing concepts."""
        # Core quantum algorithm patterns
        self.algorithms = {
            "bell_state": {
                "description": "Creates maximum entanglement between two qubits",
                "pattern": "Apply Hadamard to first qubit, then CNOT with first as control",
                "gates": ["Hadamard", "CNOT"],
                "qubits": 2,
                "applications": ["quantum teleportation", "superdense coding"],
            },
            "ghz_state": {
                "description": "Generalization of Bell state to N qubits",
                "pattern": "Hadamard on first qubit, then chain of CNOTs",
                "gates": ["Hadamard", "CNOT"],
                "qubits": "N",
                "applications": ["quantum communication", "error correction"],
            },
            "quantum_fourier_transform": {
                "description": "Quantum version of discrete Fourier transform",
                "pattern": "Series of Hadamard and controlled phase rotations",
                "gates": ["Hadamard", "CRot", "SWAP"],
                "qubits": "N",
                "applications": ["phase estimation", "Shor's algorithm"],
            },
            "grover_diffusion": {
                "description": "Amplification step in Grover's search algorithm",
                "pattern": "Hadamard all, X all, multi-controlled Z, X all, Hadamard all",
                "gates": ["Hadamard", "PauliX", "MultiControlledZ"],
                "qubits": "N",
                "applications": ["database search", "optimization"],
            },
            "phase_estimation": {
                "description": "Estimates eigenvalue phase of a unitary operator",
                "pattern": "Hadamard on ancilla, controlled unitaries, inverse QFT",
                "gates": ["Hadamard", "ControlU", "QFT"],
                "qubits": "N + M (ancilla + system)",
                "applications": ["quantum chemistry", "factoring"],
            },
        }

        # Common gate patterns
        self.gate_patterns = {
            "superposition": {
                "gates": ["Hadamard"],
                "description": "Creates equal superposition of basis states",
            },
            "entanglement": {
                "gates": ["CNOT", "CZ"],
                "description": "Creates correlation between qubits",
            },
            "phase_flip": {
                "gates": ["PauliZ", "S", "T", "RZ"],
                "description": "Applies phase to quantum state",
            },
            "bit_flip": {
                "gates": ["PauliX", "RX"],
                "description": "Rotates state around X-axis",
            },
            "rotation": {
                "gates": ["RX", "RY", "RZ", "Rot"],
                "description": "Arbitrary single-qubit rotation",
            },
        }

        # PennyLane-specific concepts
        self.pennylane_concepts = {
            "measurements": {
                "state": "Returns full quantum state vector",
                "probs": "Returns probability distribution over basis states",
                "expval": "Returns expectation value of observable",
                "sample": "Returns measurement samples",
                "var": "Returns variance of observable",
            },
            "devices": {
                "default.qubit": "Statevector simulator for exact simulation",
                "default.mixed": "Density matrix simulator for mixed states",
                "lightning.qubit": "High-performance simulator",
            },
            "templates": {
                "description": "Pre-built circuit templates in PennyLane",
                "examples": [
                    "AngleEmbedding",
                    "StronglyEntanglingLayers",
                    "BasicEntanglerLayers",
                ],
            },
        }

        # Common quantum computing terminology
        self.terminology = {
            "superposition": "Quantum state that is a linear combination of basis states",
            "entanglement": "Quantum correlation that cannot be described classically",
            "interference": "Amplification/cancellation of probability amplitudes",
            "oracle": "Black-box function implemented as a unitary operator",
            "ancilla": "Helper qubit used in quantum algorithms",
            "variational": "Parameterized circuit optimized via classical-quantum loop",
        }

    def search(
        self, query: str, top_k: int = 3, include_patterns: bool = True
    ) -> List[Dict[str, str]]:
        """
        Search the knowledge base for relevant quantum computing concepts.

        Args:
            query: Natural language query about quantum circuits.
            top_k: Number of top results to return.
            include_patterns: Whether to include gate patterns in results.

        Returns:
            List of relevant knowledge entries with descriptions.
        """
        results = []
        query_lower = query.lower()

        # Search algorithms
        for algo_name, algo_info in self.algorithms.items():
            score = self._compute_relevance(query_lower, algo_name, algo_info)
            if score > 0:
                results.append(
                    {
                        "type": "algorithm",
                        "name": algo_name,
                        "description": algo_info["description"],
                        "pattern": algo_info["pattern"],
                        "gates": ", ".join(algo_info["gates"]),
                        "applications": ", ".join(algo_info["applications"]),
                        "score": score,
                    }
                )

        # Search gate patterns if requested
        if include_patterns:
            for pattern_name, pattern_info in self.gate_patterns.items():
                score = self._compute_relevance(query_lower, pattern_name, pattern_info)
                if score > 0:
                    results.append(
                        {
                            "type": "pattern",
                            "name": pattern_name,
                            "description": pattern_info["description"],
                            "gates": ", ".join(pattern_info["gates"]),
                            "score": score,
                        }
                    )

        # Search terminology
        for term, definition in self.terminology.items():
            if term in query_lower:
                results.append(
                    {
                        "type": "concept",
                        "name": term,
                        "description": definition,
                        "score": 2.0,  # Higher score for exact term matches
                    }
                )

        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _compute_relevance(self, query: str, name: str, info: Dict[str, Any]) -> float:
        """
        Compute relevance score between query and knowledge entry.

        Args:
            query: Search query (lowercase).
            name: Entry name.
            info: Entry information dictionary.

        Returns:
            Relevance score (higher is more relevant).
        """
        score = 0.0

        # Exact name match
        if name.replace("_", " ") in query:
            score += 3.0

        # Partial name match
        name_words = name.split("_")
        for word in name_words:
            if word in query:
                score += 1.0

        # Description match
        if "description" in info:
            desc_lower = info["description"].lower()
            desc_words = desc_lower.split()
            for word in desc_words:
                if word in query and len(word) > 3:
                    score += 0.5

        # Gate match
        if "gates" in info:
            for gate in info["gates"]:
                if gate.lower() in query:
                    score += 1.5

        # Application match
        if "applications" in info:
            for app in info["applications"]:
                if app in query:
                    score += 1.0

        return score

    def get_measurement_guidance(self, query: str) -> Optional[str]:
        """
        Provide guidance on appropriate measurement type.

        Args:
            query: Circuit description query.

        Returns:
            Recommended measurement type and explanation.
        """
        query_lower = query.lower()

        if any(
            word in query_lower for word in ["probability", "probabilities", "prob"]
        ):
            return "qml.probs() - Returns probability distribution over computational basis"
        elif any(
            word in query_lower for word in ["expectation", "expval", "observable"]
        ):
            return "qml.expval() - Returns expectation value of an observable"
        elif any(word in query_lower for word in ["sample", "samples", "measurements"]):
            return "qml.sample() - Returns measurement samples"
        elif any(
            word in query_lower for word in ["state", "statevector", "amplitudes"]
        ):
            return "qml.state() - Returns full quantum state vector"
        else:
            return "qml.state() - Default: returns full quantum state vector"

    def get_context(self, query: str) -> str:
        """
        Get formatted context string for circuit generation.

        Args:
            query: Circuit description query.

        Returns:
            Formatted knowledge context as a string.
        """
        results = self.search(query, top_k=3)
        measurement_guide = self.get_measurement_guidance(query)

        context_parts = []

        if results:
            context_parts.append("## Relevant Quantum Concepts:")
            for result in results:
                if result["type"] == "algorithm":
                    context_parts.append(
                        f"\n**{result['name'].replace('_', ' ').title()}**"
                    )
                    context_parts.append(f"- {result['description']}")
                    context_parts.append(f"- Pattern: {result['pattern']}")
                    context_parts.append(f"- Key gates: {result['gates']}")
                elif result["type"] == "pattern":
                    context_parts.append(
                        f"\n**{result['name'].replace('_', ' ').title()} Pattern**"
                    )
                    context_parts.append(f"- {result['description']}")
                    context_parts.append(f"- Gates: {result['gates']}")
                elif result["type"] == "concept":
                    context_parts.append(
                        f"\n**{result['name'].title()}**: {result['description']}"
                    )

        if measurement_guide:
            context_parts.append(
                f"\n## Measurement Recommendation:\n{measurement_guide}"
            )

        return "\n".join(context_parts) if context_parts else ""
