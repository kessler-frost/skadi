"""Circuit transformation operations using PennyLane's transform system."""

from functools import partial
from typing import Any, Callable, Dict, Optional

import pennylane as qml
from pennylane import transforms

from skadi.core.circuit_representation import CircuitRepresentation


class CircuitTransformer:
    """Apply PennyLane quantum transforms to circuits.

    This class provides a convenient interface to PennyLane's built-in
    transform system, allowing circuits to be decomposed, simplified,
    and optimized using various transformation operations.

    Available Transforms:
        - cancel_inverses: Remove adjacent inverse gate pairs
        - merge_rotations: Combine adjacent rotations of the same type
        - commute_controlled: Push single-qubit gates through controlled operations
        - decompose: Decompose operations to a specific gate set
        - simplify: Apply algebraic simplification
        - transpile: Compile for specific hardware topology
        - adjoint: Create adjoint/inverse of circuit

    Example:
        >>> transformer = CircuitTransformer()
        >>> optimized = transformer.apply_transform(circuit, "cancel_inverses")
        >>> print(optimized.transform_history)
    """

    # Registry of available transforms with their functions
    TRANSFORMS: Dict[str, Callable] = {
        "cancel_inverses": transforms.cancel_inverses,
        "merge_rotations": transforms.merge_rotations,
        "commute_controlled": transforms.commute_controlled,
        "simplify": qml.simplify,
        "adjoint": qml.adjoint,
    }

    # Transforms that require additional parameters
    PARAMETERIZED_TRANSFORMS: Dict[str, Callable] = {
        "decompose": transforms.decompose,
        "transpile": transforms.transpile,
    }

    def __init__(self):
        """Initialize the circuit transformer."""
        self.all_transforms = {**self.TRANSFORMS, **self.PARAMETERIZED_TRANSFORMS}

    def list_transforms(self) -> list[str]:
        """Get list of available transform names.

        Returns:
            List of transform names that can be applied
        """
        return list(self.all_transforms.keys())

    def apply_transform(
        self,
        circuit: CircuitRepresentation,
        transform_name: str,
        **kwargs: Any,
    ) -> CircuitRepresentation:
        """Apply a transformation to a circuit.

        Args:
            circuit: CircuitRepresentation to transform
            transform_name: Name of transform to apply
            **kwargs: Additional parameters for the transform

        Returns:
            New CircuitRepresentation with transform applied

        Raises:
            ValueError: If transform_name is not recognized or circuit has no qnode
            KeyError: If required parameters for transform are missing

        Example:
            >>> transformer = CircuitTransformer()
            >>> # Simple transform
            >>> optimized = transformer.apply_transform(circuit, "cancel_inverses")
            >>>
            >>> # Parameterized transform
            >>> decomposed = transformer.apply_transform(
            ...     circuit,
            ...     "decompose",
            ...     gate_set={"Hadamard", "CNOT", "RZ"}
            ... )
        """
        if circuit.qnode is None:
            raise ValueError("Circuit must have a qnode to apply transforms")

        if transform_name not in self.all_transforms:
            available = ", ".join(self.list_transforms())
            raise ValueError(
                f"Unknown transform '{transform_name}'. "
                f"Available transforms: {available}"
            )

        # Get specs before transformation
        before_specs = circuit.get_specs()

        # Get the transform function
        transform_func = self.all_transforms[transform_name]

        # Apply transform with parameters if provided
        if kwargs:
            transform_func = partial(transform_func, **kwargs)

        # Apply transform to qnode
        transformed_qnode = transform_func(circuit.qnode)

        # Create new circuit representation
        new_circuit = circuit.clone(qnode=transformed_qnode)

        # Get specs after transformation
        after_specs = new_circuit.get_specs()

        # Record transformation in history
        new_circuit.add_transform(
            transform_name=transform_name,
            transform_params=kwargs,
            before_specs=before_specs,
            after_specs=after_specs,
        )

        return new_circuit

    def apply_sequence(
        self,
        circuit: CircuitRepresentation,
        transforms: list[tuple[str, Optional[Dict[str, Any]]]],
    ) -> CircuitRepresentation:
        """Apply a sequence of transformations.

        Args:
            circuit: CircuitRepresentation to transform
            transforms: List of (transform_name, kwargs) tuples

        Returns:
            CircuitRepresentation with all transforms applied in order

        Example:
            >>> transformer = CircuitTransformer()
            >>> transforms_seq = [
            ...     ("cancel_inverses", None),
            ...     ("merge_rotations", None),
            ...     ("simplify", None),
            ... ]
            >>> result = transformer.apply_sequence(circuit, transforms_seq)
        """
        current = circuit

        for transform_name, params in transforms:
            kwargs = params or {}
            current = self.apply_transform(current, transform_name, **kwargs)

        return current

    def get_transform_info(self, transform_name: str) -> Dict[str, Any]:
        """Get information about a specific transform.

        Args:
            transform_name: Name of the transform

        Returns:
            Dictionary with transform details

        Raises:
            ValueError: If transform_name is not recognized
        """
        if transform_name not in self.all_transforms:
            raise ValueError(f"Unknown transform: {transform_name}")

        transform_func = self.all_transforms[transform_name]

        info = {
            "name": transform_name,
            "function": transform_func.__name__,
            "module": transform_func.__module__,
            "parameterized": transform_name in self.PARAMETERIZED_TRANSFORMS,
        }

        # Add docstring if available
        if transform_func.__doc__:
            info["description"] = transform_func.__doc__.split("\n")[0].strip()

        return info
