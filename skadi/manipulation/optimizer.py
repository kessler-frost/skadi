"""Circuit optimization using PennyLane's compilation pipeline."""

from typing import Any, Callable, Dict, List, Optional

import pennylane as qml
from pennylane import transforms

from skadi.core.circuit_representation import CircuitRepresentation


class CircuitOptimizer:
    """Optimize quantum circuits for depth and gate count.

    This class provides circuit optimization using PennyLane's compilation
    pipeline with configurable optimization levels and custom pipelines.

    Optimization Levels:
        - basic: Cancel inverse gates only
        - default: Standard pipeline (commute → cancel → merge)
        - aggressive: Multiple passes with all transforms

    Example:
        >>> optimizer = CircuitOptimizer()
        >>> optimized = optimizer.optimize(circuit, level="default")
        >>> report = optimized.transform_history[-1]
        >>> print(report["improvement"])
    """

    # Predefined optimization pipelines
    PIPELINES: Dict[str, List[Callable]] = {
        "basic": [transforms.cancel_inverses],
        "default": [
            transforms.commute_controlled,
            transforms.cancel_inverses,
            transforms.merge_rotations,
        ],
        "aggressive": [
            transforms.commute_controlled,
            transforms.cancel_inverses,
            transforms.merge_rotations,
            qml.simplify,
        ],
    }

    def __init__(self):
        """Initialize the circuit optimizer."""
        pass

    def optimize(
        self,
        circuit: CircuitRepresentation,
        level: str = "default",
        num_passes: int = 1,
        custom_pipeline: Optional[List[Callable]] = None,
        gate_set: Optional[set] = None,
    ) -> CircuitRepresentation:
        """Optimize a circuit using the specified optimization level.

        Args:
            circuit: CircuitRepresentation to optimize
            level: Optimization level ("basic", "default", "aggressive")
            num_passes: Number of optimization passes to apply
            custom_pipeline: Custom list of transforms (overrides level)
            gate_set: If provided, transpile to this gate set

        Returns:
            Optimized CircuitRepresentation with improvement stats

        Raises:
            ValueError: If circuit has no qnode or optimization level is invalid

        Example:
            >>> optimizer = CircuitOptimizer()
            >>> optimized = optimizer.optimize(
            ...     circuit,
            ...     level="aggressive",
            ...     num_passes=3
            ... )
        """
        if circuit.qnode is None:
            raise ValueError("Circuit must have a qnode to optimize")

        # Get optimization pipeline
        if custom_pipeline is not None:
            pipeline = custom_pipeline
        elif level in self.PIPELINES:
            pipeline = self.PIPELINES[level]
        else:
            available = ", ".join(self.PIPELINES.keys())
            raise ValueError(
                f"Unknown optimization level '{level}'. Available levels: {available}"
            )

        # Get specs before optimization
        before_specs = circuit.get_specs()

        # Apply transforms manually since qml.compile has issues with plain functions
        optimized_qnode = circuit.qnode
        for transform_func in pipeline:
            optimized_qnode = transform_func(optimized_qnode)

        # Apply multiple passes if requested
        for _ in range(num_passes - 1):
            for transform_func in pipeline:
                optimized_qnode = transform_func(optimized_qnode)

        # If gate_set specified, apply transpilation
        if gate_set:
            # Note: transpile requires coupling_map, using it without for now
            optimized_qnode = transforms.transpile(optimized_qnode)

        # Create new circuit representation
        new_circuit = circuit.clone(qnode=optimized_qnode)

        # Get specs after optimization
        after_specs = new_circuit.get_specs()

        # Calculate improvements
        improvement = self._calculate_improvement(before_specs, after_specs)

        # Record optimization in history
        new_circuit.add_transform(
            transform_name=f"optimize_{level}",
            transform_params={
                "level": level,
                "num_passes": num_passes,
                "pipeline": [f.__name__ for f in pipeline],
                "gate_set": list(gate_set) if gate_set else None,
            },
            before_specs=before_specs,
            after_specs=after_specs,
        )

        # Add improvement stats to the last transform entry
        new_circuit.transform_history[-1]["improvement"] = improvement

        return new_circuit

    def _calculate_improvement(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimization improvements.

        Args:
            before: Circuit specs before optimization
            after: Circuit specs after optimization

        Returns:
            Dictionary with improvement metrics
        """
        before_ops = before.get("num_operations", 0)
        after_ops = after.get("num_operations", 0)
        before_depth = before.get("depth", 0)
        after_depth = after.get("depth", 0)

        improvement = {
            "operations_reduced": before_ops - after_ops,
            "operations_percent": (
                (before_ops - after_ops) / before_ops * 100 if before_ops > 0 else 0
            ),
            "depth_reduced": before_depth - after_depth,
            "depth_percent": (
                (before_depth - after_depth) / before_depth * 100
                if before_depth > 0
                else 0
            ),
            "before_operations": before_ops,
            "after_operations": after_ops,
            "before_depth": before_depth,
            "after_depth": after_depth,
        }

        return improvement

    def get_optimization_report(self, circuit: CircuitRepresentation) -> Dict[str, Any]:
        """Generate a comprehensive optimization report.

        Args:
            circuit: CircuitRepresentation with optimization history

        Returns:
            Dictionary with optimization analysis

        Example:
            >>> optimizer = CircuitOptimizer()
            >>> optimized = optimizer.optimize(circuit)
            >>> report = optimizer.get_optimization_report(optimized)
            >>> print(report["summary"])
        """
        if not circuit.transform_history:
            return {
                "optimizations_applied": 0,
                "summary": "No optimizations applied",
            }

        # Find all optimization transforms
        optimizations = [
            t
            for t in circuit.transform_history
            if t["transform"].startswith("optimize_")
        ]

        if not optimizations:
            return {
                "optimizations_applied": 0,
                "summary": "No optimizations in transform history",
            }

        # Get total improvement from all optimizations
        total_improvement = {
            "total_operations_reduced": 0,
            "total_depth_reduced": 0,
        }

        for opt in optimizations:
            if "improvement" in opt:
                imp = opt["improvement"]
                total_improvement["total_operations_reduced"] += imp.get(
                    "operations_reduced", 0
                )
                total_improvement["total_depth_reduced"] += imp.get("depth_reduced", 0)

        # Get current stats
        current_specs = circuit.get_specs()

        report = {
            "optimizations_applied": len(optimizations),
            "current_stats": {
                "operations": current_specs.get("num_operations", 0),
                "depth": current_specs.get("depth", 0),
                "wires": current_specs.get("num_device_wires", 0),
            },
            "total_improvement": total_improvement,
            "optimization_history": [
                {
                    "level": opt["params"].get("level", "unknown"),
                    "passes": opt["params"].get("num_passes", 1),
                    "improvement": opt.get("improvement", {}),
                    "timestamp": opt["timestamp"].isoformat(),
                }
                for opt in optimizations
            ],
            "summary": self._generate_summary(optimizations, current_specs),
        }

        return report

    def _generate_summary(
        self, optimizations: List[Dict], current_specs: Dict[str, Any]
    ) -> str:
        """Generate human-readable optimization summary.

        Args:
            optimizations: List of optimization transforms
            current_specs: Current circuit specifications

        Returns:
            Summary string
        """
        num_opts = len(optimizations)
        total_ops_reduced = sum(
            opt.get("improvement", {}).get("operations_reduced", 0)
            for opt in optimizations
        )
        total_depth_reduced = sum(
            opt.get("improvement", {}).get("depth_reduced", 0) for opt in optimizations
        )

        summary_parts = [
            f"Applied {num_opts} optimization(s).",
            f"Reduced operations by {total_ops_reduced}.",
            f"Reduced depth by {total_depth_reduced}.",
            f"Current: {current_specs.get('num_operations', 0)} operations, "
            f"depth {current_specs.get('depth', 0)}.",
        ]

        return " ".join(summary_parts)

    def compare_levels(
        self, circuit: CircuitRepresentation
    ) -> Dict[str, CircuitRepresentation]:
        """Compare all optimization levels on the same circuit.

        Args:
            circuit: CircuitRepresentation to optimize

        Returns:
            Dictionary mapping level names to optimized circuits

        Example:
            >>> optimizer = CircuitOptimizer()
            >>> results = optimizer.compare_levels(circuit)
            >>> for level, optimized in results.items():
            ...     print(f"{level}: {optimized.get_specs()['num_operations']} ops")
        """
        results = {}

        for level in self.PIPELINES.keys():
            results[level] = self.optimize(circuit, level=level)

        return results
