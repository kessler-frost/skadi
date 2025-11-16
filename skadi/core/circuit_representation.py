"""Circuit representation with metadata and transformation tracking."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import pennylane as qml


class CircuitRepresentation:
    """Unified representation of quantum circuits with metadata and history tracking.

    This class wraps a PennyLane QNode along with its generated code, original
    description, and transformation history to enable comprehensive circuit
    manipulation and analysis.

    Attributes:
        qnode: Executable PennyLane QNode function
        code: Generated Python code string
        description: Original natural language description
        metadata: Additional metadata (generation params, timestamps, etc.)
        transform_history: List of applied transformations with before/after stats

    Example:
        >>> circuit = CircuitRepresentation(
        ...     qnode=my_qnode,
        ...     code=generated_code,
        ...     description="Create a Bell state"
        ... )
        >>> specs = circuit.get_specs()
        >>> print(circuit.transform_history)
    """

    def __init__(
        self,
        qnode: Optional[Callable] = None,
        code: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize circuit representation.

        Args:
            qnode: Executable PennyLane QNode function
            code: Generated Python code string
            description: Original natural language description
            metadata: Additional metadata dictionary
        """
        self.qnode = qnode
        self.code = code
        self.description = description
        self.metadata = metadata or {}
        self.transform_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()

        # Cache for tape and specs to avoid recomputation
        self._tape: Optional[Any] = None
        self._specs: Optional[Dict[str, Any]] = None

    def get_tape(self, refresh: bool = False) -> Any:
        """Get the quantum tape by executing the circuit once.

        The tape is cached after first execution unless refresh=True.

        Args:
            refresh: If True, force re-execution to get fresh tape

        Returns:
            QuantumTape object containing circuit operations

        Raises:
            ValueError: If qnode is not set
        """
        if self.qnode is None:
            raise ValueError("QNode is not set, cannot retrieve tape")

        if self._tape is None or refresh:
            # Execute to construct tape
            _ = self.qnode()
            # Access the tape through the qnode's tape attribute
            self._tape = getattr(self.qnode, "tape", getattr(self.qnode, "_tape", None))

        return self._tape

    def get_specs(self, refresh: bool = False) -> Dict[str, Any]:
        """Get circuit specifications using qml.specs.

        Specifications include gate counts, depth, wires, trainable parameters,
        and other circuit properties. Results are cached unless refresh=True.

        Args:
            refresh: If True, force recomputation of specs

        Returns:
            Dictionary containing circuit specifications

        Raises:
            ValueError: If qnode is not set
        """
        if self.qnode is None:
            raise ValueError("QNode is not set, cannot retrieve specs")

        if self._specs is None or refresh:
            self._specs = qml.specs(self.qnode)()

        return self._specs

    def get_visualization(self, level: int = 0, **kwargs) -> str:
        """Get text-based circuit visualization.

        Args:
            level: Expansion level for drawing (0=user program, higher=more expanded)
            **kwargs: Additional arguments passed to qml.draw()

        Returns:
            String representation of circuit diagram

        Raises:
            ValueError: If qnode is not set
        """
        if self.qnode is None:
            raise ValueError("QNode is not set, cannot visualize")

        drawer = qml.draw(self.qnode, level=level, **kwargs)
        return drawer()

    def add_transform(
        self,
        transform_name: str,
        transform_params: Optional[Dict[str, Any]] = None,
        before_specs: Optional[Dict[str, Any]] = None,
        after_specs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a transformation in the history.

        Args:
            transform_name: Name of the transform applied
            transform_params: Parameters used for the transform
            before_specs: Circuit specs before transformation
            after_specs: Circuit specs after transformation
        """
        self.transform_history.append(
            {
                "transform": transform_name,
                "params": transform_params or {},
                "before": before_specs,
                "after": after_specs,
                "timestamp": datetime.now(),
            }
        )

        # Invalidate cached specs after transformation
        self._specs = None
        self._tape = None

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get a summary of circuit resources.

        Returns:
            Dictionary with gate counts, depth, and wire information
        """
        specs = self.get_specs()

        # Extract from resources object
        resources = specs["resources"]

        return {
            "num_operations": resources.num_gates,
            "depth": resources.depth,
            "num_wires": specs["num_device_wires"],
            "num_trainable_params": specs["num_trainable_params"],
            "gate_types": dict(resources.gate_types),
            "gate_sizes": dict(resources.gate_sizes),
        }

    def clone(
        self, qnode: Optional[Callable] = None, code: Optional[str] = None
    ) -> "CircuitRepresentation":
        """Create a copy of this representation with optional updates.

        Args:
            qnode: New QNode to use (if None, keeps current)
            code: New code to use (if None, keeps current)

        Returns:
            New CircuitRepresentation instance
        """
        new_repr = CircuitRepresentation(
            qnode=qnode or self.qnode,
            code=code or self.code,
            description=self.description,
            metadata=self.metadata.copy(),
        )

        # Copy transform history
        new_repr.transform_history = self.transform_history.copy()

        return new_repr

    def __repr__(self) -> str:
        """String representation of circuit."""
        parts = ["CircuitRepresentation("]

        if self.description:
            parts.append(f"description='{self.description[:50]}...'")

        if self.qnode:
            specs = self.get_specs()
            parts.append(
                f"ops={specs.get('num_operations', 0)}, "
                f"depth={specs.get('depth', 0)}, "
                f"wires={specs.get('num_device_wires', 0)}"
            )

        if self.transform_history:
            parts.append(f"transforms={len(self.transform_history)}")

        return ", ".join(parts) + ")"
