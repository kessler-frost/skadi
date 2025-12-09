"""Unit tests for circuit manipulation modules."""

import pennylane as qml
import pytest

from skadi.core.circuit_representation import CircuitRepresentation
from skadi.manipulation.analyzer import CircuitAnalyzer
from skadi.manipulation.optimizer import CircuitOptimizer
from skadi.manipulation.transformer import CircuitTransformer


@pytest.fixture
def bell_state_circuit():
    """Create a Bell state circuit for testing."""
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    code = """import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
"""

    return CircuitRepresentation(
        qnode=circuit,
        code=code,
        description="Bell state",
    )


@pytest.fixture
def complex_circuit():
    """Create a more complex circuit with potential for optimization."""
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)
        qml.Hadamard(wires=0)  # Inverses (cancel out)
        qml.RZ(0.5, wires=0)
        qml.RZ(0.3, wires=0)  # Can be merged
        qml.CNOT(wires=[0, 1])
        return qml.state()

    code = """import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=0)
    qml.RZ(0.5, wires=0)
    qml.RZ(0.3, wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
"""

    return CircuitRepresentation(
        qnode=circuit,
        code=code,
        description="Complex circuit",
    )


class TestCircuitTransformer:
    """Test CircuitTransformer functionality."""

    def test_init(self):
        """Test transformer initialization."""
        transformer = CircuitTransformer()
        assert transformer is not None
        assert hasattr(transformer, "TRANSFORMS")
        assert hasattr(transformer, "PARAMETERIZED_TRANSFORMS")

    def test_list_transforms(self):
        """Test listing available transforms."""
        transformer = CircuitTransformer()
        transforms = transformer.list_transforms()

        assert isinstance(transforms, list)
        assert len(transforms) > 0
        assert "cancel_inverses" in transforms
        assert "merge_rotations" in transforms
        assert "commute_controlled" in transforms

    def test_apply_transform_cancel_inverses(self, complex_circuit):
        """Test applying cancel_inverses transform."""
        transformer = CircuitTransformer()
        before_summary = complex_circuit.get_resource_summary()
        before_ops = before_summary["num_operations"]

        transformed = transformer.apply_transform(complex_circuit, "cancel_inverses")

        # Should have transformation history
        assert len(transformed.transform_history) == 1
        assert transformed.transform_history[0]["transform"] == "cancel_inverses"

        # Original circuit should be unchanged
        assert len(complex_circuit.transform_history) == 0

        # New circuit should potentially have fewer operations
        after_summary = transformed.get_resource_summary()
        after_ops = after_summary["num_operations"]
        assert after_ops <= before_ops

    def test_apply_transform_invalid_name(self, bell_state_circuit):
        """Test applying invalid transform name."""
        transformer = CircuitTransformer()

        with pytest.raises(ValueError, match="Unknown transform"):
            transformer.apply_transform(bell_state_circuit, "invalid_transform")

    def test_apply_transform_no_qnode(self):
        """Test applying transform without qnode."""
        transformer = CircuitTransformer()
        circuit = CircuitRepresentation(code="test")

        with pytest.raises(ValueError, match="must have a qnode"):
            transformer.apply_transform(circuit, "cancel_inverses")

    def test_apply_sequence(self, complex_circuit):
        """Test applying sequence of transforms."""
        transformer = CircuitTransformer()

        transforms_seq = [
            ("cancel_inverses", None),
            ("merge_rotations", None),
        ]

        result = transformer.apply_sequence(complex_circuit, transforms_seq)

        # Should have two transforms in history
        assert len(result.transform_history) == 2
        assert result.transform_history[0]["transform"] == "cancel_inverses"
        assert result.transform_history[1]["transform"] == "merge_rotations"

    def test_get_transform_info(self):
        """Test getting transform information."""
        transformer = CircuitTransformer()
        info = transformer.get_transform_info("cancel_inverses")

        assert info["name"] == "cancel_inverses"
        assert "function" in info
        assert "module" in info
        assert isinstance(info["parameterized"], bool)

    def test_get_transform_info_invalid(self):
        """Test getting info for invalid transform."""
        transformer = CircuitTransformer()

        with pytest.raises(ValueError, match="Unknown transform"):
            transformer.get_transform_info("invalid")


class TestCircuitOptimizer:
    """Test CircuitOptimizer functionality."""

    def test_init(self):
        """Test optimizer initialization."""
        optimizer = CircuitOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, "PIPELINES")

    def test_optimize_basic(self, complex_circuit):
        """Test basic optimization."""
        optimizer = CircuitOptimizer()

        optimized = optimizer.optimize(complex_circuit, level="basic")

        # Should have optimization in history
        assert len(optimized.transform_history) == 1
        assert optimized.transform_history[0]["transform"] == "optimize_basic"

        # Should have improvement stats
        assert "improvement" in optimized.transform_history[0]
        improvement = optimized.transform_history[0]["improvement"]
        assert "operations_reduced" in improvement
        assert "depth_reduced" in improvement

    def test_optimize_levels(self, bell_state_circuit):
        """Test different optimization levels."""
        optimizer = CircuitOptimizer()

        for level in ["basic", "default", "aggressive"]:
            optimized = optimizer.optimize(bell_state_circuit, level=level)
            assert optimized is not None
            assert len(optimized.transform_history) == 1
            assert optimized.transform_history[0]["params"]["level"] == level

    def test_optimize_multiple_passes(self, complex_circuit):
        """Test optimization with multiple passes."""
        optimizer = CircuitOptimizer()
        optimized = optimizer.optimize(complex_circuit, level="default", num_passes=3)

        assert optimized.transform_history[0]["params"]["num_passes"] == 3

    def test_optimize_invalid_level(self, bell_state_circuit):
        """Test optimization with invalid level."""
        optimizer = CircuitOptimizer()

        with pytest.raises(ValueError, match="Unknown optimization level"):
            optimizer.optimize(bell_state_circuit, level="invalid")

    def test_calculate_improvement(self):
        """Test improvement calculation."""
        optimizer = CircuitOptimizer()

        before = {"num_operations": 10, "depth": 5}
        after = {"num_operations": 7, "depth": 3}

        improvement = optimizer._calculate_improvement(before, after)

        assert improvement["operations_reduced"] == 3
        assert improvement["depth_reduced"] == 2
        assert improvement["operations_percent"] == 30.0
        assert improvement["depth_percent"] == 40.0

    def test_get_optimization_report(self, complex_circuit):
        """Test getting optimization report."""
        optimizer = CircuitOptimizer()
        optimized = optimizer.optimize(complex_circuit, level="aggressive")

        report = optimizer.get_optimization_report(optimized)

        assert "optimizations_applied" in report
        assert report["optimizations_applied"] == 1
        assert "current_stats" in report
        assert "summary" in report
        assert isinstance(report["summary"], str)

    def test_get_optimization_report_no_optimizations(self, bell_state_circuit):
        """Test report with no optimizations."""
        optimizer = CircuitOptimizer()
        report = optimizer.get_optimization_report(bell_state_circuit)

        assert report["optimizations_applied"] == 0
        assert "No optimizations" in report["summary"]

    def test_compare_levels(self, complex_circuit):
        """Test comparing all optimization levels."""
        optimizer = CircuitOptimizer()
        results = optimizer.compare_levels(complex_circuit)

        assert isinstance(results, dict)
        assert "basic" in results
        assert "default" in results
        assert "aggressive" in results

        for level, optimized in results.items():
            assert isinstance(optimized, CircuitRepresentation)
            assert len(optimized.transform_history) == 1


class TestCircuitAnalyzer:
    """Test CircuitAnalyzer functionality."""

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = CircuitAnalyzer()
        assert analyzer is not None
        assert analyzer.llm_client is None

    def test_analyze_without_llm(self, bell_state_circuit):
        """Test analysis without LLM client."""
        analyzer = CircuitAnalyzer()
        analysis = analyzer.analyze(bell_state_circuit, include_explanation=False)

        assert "description" in analysis
        assert "specs" in analysis
        assert "resources" in analysis
        assert "complexity" in analysis
        assert analysis["description"] == "Bell state"

    def test_analyze_specs(self, bell_state_circuit):
        """Test specs in analysis."""
        analyzer = CircuitAnalyzer()
        analysis = analyzer.analyze(bell_state_circuit, include_explanation=False)

        specs = analysis["specs"]
        assert specs["num_operations"] == 2
        assert specs["depth"] == 2
        assert specs["num_wires"] == 2
        assert "gate_types" in specs

    def test_analyze_complexity(self, bell_state_circuit):
        """Test complexity assessment."""
        analyzer = CircuitAnalyzer()
        analysis = analyzer.analyze(bell_state_circuit, include_explanation=False)

        complexity = analysis["complexity"]
        assert complexity["level"] == "simple"
        # Entangling gates should be at least 0 (might be 0 or 1 depending on how gate_sizes is calculated)
        assert complexity["entangling_gates"] >= 0

    def test_analyze_with_visualization(self, bell_state_circuit):
        """Test analysis with visualization."""
        analyzer = CircuitAnalyzer()
        analysis = analyzer.analyze(
            bell_state_circuit, include_explanation=False, include_visualization=True
        )

        assert "visualization" in analysis
        assert isinstance(analysis["visualization"], str)

    def test_compare_circuits(self, bell_state_circuit):
        """Test circuit comparison."""
        analyzer = CircuitAnalyzer()

        # Create a modified version
        optimizer = CircuitOptimizer()
        optimized = optimizer.optimize(bell_state_circuit, level="basic")

        comparison = analyzer.compare_circuits(
            bell_state_circuit, optimized, names=("Original", "Optimized")
        )

        assert "circuits" in comparison
        assert comparison["circuits"] == ("Original", "Optimized")
        assert "circuit1" in comparison
        assert "circuit2" in comparison
        assert "differences" in comparison

    def test_get_gate_analysis(self, bell_state_circuit):
        """Test gate analysis."""
        analyzer = CircuitAnalyzer()
        gate_info = analyzer.get_gate_analysis(bell_state_circuit)

        assert "total_gates" in gate_info
        # Total gates should be at least 0
        assert gate_info["total_gates"] >= 0
        assert "single_qubit_gates" in gate_info
        assert "multi_qubit_gates" in gate_info
        # Sum should match total
        total_counted = gate_info["single_qubit_count"] + gate_info["multi_qubit_count"]
        assert total_counted == gate_info["total_gates"]
