"""Context7 client for fetching PennyLane API documentation."""

from typing import List


class Context7Client:
    """
    Client for fetching PennyLane documentation from Context7 via Claude MCP.

    Provides API-specific details, function signatures, and code examples
    to augment circuit generation with accurate PennyLane syntax.
    """

    def __init__(self):
        """
        Initialize the Context7 client.

        Note:
            This uses a built-in knowledge base of PennyLane documentation.
            In a full implementation, this would use the Context7 MCP protocol.
        """
        # Note: In a full implementation, this would use the MCP protocol
        # For now, we use a static knowledge base of PennyLane documentation
        self._initialize_pennylane_docs()

    def _initialize_pennylane_docs(self) -> None:
        """Initialize PennyLane API documentation knowledge."""
        # This is a simplified version. In production, this would query Context7 MCP
        self.api_docs = {
            "qml.Hadamard": {
                "signature": "qml.Hadamard(wires)",
                "description": "Applies the Hadamard gate to a qubit",
                "parameters": ["wires: int or list - wire(s) to apply the gate to"],
                "example": "qml.Hadamard(wires=0)",
                "category": "single_qubit",
            },
            "qml.CNOT": {
                "signature": "qml.CNOT(wires)",
                "description": "Applies the controlled-NOT (CNOT) gate",
                "parameters": [
                    "wires: list[int] - [control_wire, target_wire]",
                ],
                "example": "qml.CNOT(wires=[0, 1])",
                "category": "two_qubit",
            },
            "qml.PauliX": {
                "signature": "qml.PauliX(wires)",
                "description": "Applies the Pauli-X (bit-flip) gate",
                "parameters": ["wires: int or list - wire(s) to apply the gate to"],
                "example": "qml.PauliX(wires=0)",
                "category": "single_qubit",
            },
            "qml.PauliY": {
                "signature": "qml.PauliY(wires)",
                "description": "Applies the Pauli-Y gate",
                "parameters": ["wires: int or list - wire(s) to apply the gate to"],
                "example": "qml.PauliY(wires=0)",
                "category": "single_qubit",
            },
            "qml.PauliZ": {
                "signature": "qml.PauliZ(wires)",
                "description": "Applies the Pauli-Z (phase-flip) gate",
                "parameters": ["wires: int or list - wire(s) to apply the gate to"],
                "example": "qml.PauliZ(wires=0)",
                "category": "single_qubit",
            },
            "qml.RX": {
                "signature": "qml.RX(phi, wires)",
                "description": "Applies rotation around X-axis",
                "parameters": [
                    "phi: float - rotation angle in radians",
                    "wires: int or list - wire(s) to apply the gate to",
                ],
                "example": "qml.RX(0.5, wires=0)",
                "category": "rotation",
            },
            "qml.RY": {
                "signature": "qml.RY(phi, wires)",
                "description": "Applies rotation around Y-axis",
                "parameters": [
                    "phi: float - rotation angle in radians",
                    "wires: int or list - wire(s) to apply the gate to",
                ],
                "example": "qml.RY(0.5, wires=0)",
                "category": "rotation",
            },
            "qml.RZ": {
                "signature": "qml.RZ(phi, wires)",
                "description": "Applies rotation around Z-axis",
                "parameters": [
                    "phi: float - rotation angle in radians",
                    "wires: int or list - wire(s) to apply the gate to",
                ],
                "example": "qml.RZ(0.5, wires=0)",
                "category": "rotation",
            },
            "qml.CZ": {
                "signature": "qml.CZ(wires)",
                "description": "Applies the controlled-Z gate",
                "parameters": [
                    "wires: list[int] - [control_wire, target_wire]",
                ],
                "example": "qml.CZ(wires=[0, 1])",
                "category": "two_qubit",
            },
            "qml.SWAP": {
                "signature": "qml.SWAP(wires)",
                "description": "Applies the SWAP gate to exchange two qubits",
                "parameters": [
                    "wires: list[int] - [wire1, wire2]",
                ],
                "example": "qml.SWAP(wires=[0, 1])",
                "category": "two_qubit",
            },
            "qml.Toffoli": {
                "signature": "qml.Toffoli(wires)",
                "description": "Applies the Toffoli (CCNOT) gate",
                "parameters": [
                    "wires: list[int] - [control1, control2, target]",
                ],
                "example": "qml.Toffoli(wires=[0, 1, 2])",
                "category": "multi_qubit",
            },
            "qml.device": {
                "signature": "qml.device(name, wires, **kwargs)",
                "description": "Creates a quantum device for circuit execution",
                "parameters": [
                    'name: str - device name (e.g., "default.qubit")',
                    "wires: int - number of qubits",
                    "shots: int - number of measurement shots (optional)",
                ],
                "example": 'dev = qml.device("default.qubit", wires=2)',
                "category": "device",
            },
            "qml.qnode": {
                "signature": "@qml.qnode(device)",
                "description": "Decorator to convert a quantum function into a QNode",
                "parameters": [
                    "device: Device - quantum device to execute the circuit on",
                    "interface: str - gradient computation interface (optional)",
                ],
                "example": "@qml.qnode(dev)\ndef circuit():\n    return qml.state()",
                "category": "decorator",
            },
            "qml.state": {
                "signature": "qml.state()",
                "description": "Returns the full quantum state vector",
                "parameters": [],
                "example": "return qml.state()",
                "category": "measurement",
            },
            "qml.probs": {
                "signature": "qml.probs(wires=None)",
                "description": "Returns probability distribution over basis states",
                "parameters": [
                    "wires: int, list, or None - wires to measure (None = all wires)"
                ],
                "example": "return qml.probs(wires=[0, 1])",
                "category": "measurement",
            },
            "qml.expval": {
                "signature": "qml.expval(observable)",
                "description": "Returns expectation value of an observable",
                "parameters": [
                    "observable: Observable - quantum observable to measure"
                ],
                "example": "return qml.expval(qml.PauliZ(0))",
                "category": "measurement",
            },
        }

    def get_api_docs(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Retrieve relevant API documentation for a query.

        Args:
            query: Natural language query or gate names.
            top_k: Number of top results to return.

        Returns:
            List of relevant API documentation entries.
        """
        results = []
        query_lower = query.lower()

        # Score each API entry
        for api_name, api_info in self.api_docs.items():
            score = self._compute_relevance(query_lower, api_name, api_info)
            if score > 0:
                results.append(
                    {
                        "name": api_name,
                        "signature": api_info["signature"],
                        "description": api_info["description"],
                        "parameters": api_info.get("parameters", []),
                        "example": api_info["example"],
                        "category": api_info["category"],
                        "score": score,
                    }
                )

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _compute_relevance(self, query: str, api_name: str, api_info: dict) -> float:
        """
        Compute relevance score between query and API entry.

        Args:
            query: Search query (lowercase).
            api_name: API name (e.g., "qml.Hadamard").
            api_info: API information dictionary.

        Returns:
            Relevance score.
        """
        score = 0.0

        # Extract gate name without qml. prefix
        gate_name = api_name.replace("qml.", "").lower()

        # Exact gate name match
        if gate_name in query:
            score += 5.0

        # Partial name match
        if any(word in query for word in gate_name.split("_")):
            score += 2.0

        # Category match
        category_keywords = {
            "rotation": ["rotate", "rotation", "angle", "parametric"],
            "measurement": ["measure", "measurement", "return", "output"],
            "two_qubit": ["entangle", "controlled", "cnot", "cz", "swap"],
            "single_qubit": ["hadamard", "pauli", "flip"],
            "device": ["device", "simulator", "backend"],
        }

        category = api_info.get("category", "")
        if category in category_keywords:
            for keyword in category_keywords[category]:
                if keyword in query:
                    score += 1.5

        # Description match
        desc_lower = api_info["description"].lower()
        desc_words = desc_lower.split()
        for word in desc_words:
            if word in query and len(word) > 3:
                score += 0.5

        return score

    def get_context(self, query: str, max_docs: int = 5) -> str:
        """
        Get formatted API documentation context for circuit generation.

        Args:
            query: Circuit description query.
            max_docs: Maximum number of API docs to include.

        Returns:
            Formatted API documentation as a string.
        """
        docs = self.get_api_docs(query, top_k=max_docs)

        if not docs:
            return ""

        context_parts = ["## Relevant PennyLane API:"]

        for doc in docs:
            context_parts.append(f"\n**{doc['name']}**")
            context_parts.append(f"- Signature: `{doc['signature']}`")
            context_parts.append(f"- {doc['description']}")
            if doc["parameters"]:
                context_parts.append("- Parameters:")
                for param in doc["parameters"]:
                    context_parts.append(f"  - {param}")
            context_parts.append(f"- Example: `{doc['example']}`")

        return "\n".join(context_parts)

    def fetch_docs(
        self, topic: str, context7_library_id: str = "/pennylane/pennylane"
    ) -> str:
        """
        Fetch documentation from Context7 (placeholder for future MCP integration).

        Args:
            topic: Topic to fetch documentation for.
            context7_library_id: Context7 library identifier.

        Returns:
            Documentation string.

        Note:
            This is a placeholder. In production, this would use the Anthropic MCP
            protocol to query Context7 for real-time documentation.
        """
        # For now, return static docs
        # TODO: Implement actual MCP integration with Context7
        return self.get_context(topic)
