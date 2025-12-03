"""Backend recommendation engine for Skadi."""

from dataclasses import dataclass

import psutil

from skadi.backends.base import BackendType
from skadi.backends.registry import BackendRegistry, BackendStatus
from skadi.core.circuit_representation import CircuitRepresentation


@dataclass
class SystemCapabilities:
    """Detected system capabilities."""

    total_memory_gb: float
    available_memory_gb: float
    has_gpu: bool
    gpu_memory_gb: float | None
    cpu_cores: int


@dataclass
class Recommendation:
    """Backend recommendation with reasoning."""

    backend_status: BackendStatus
    score: float  # 0-100
    reasons: list[str]
    warnings: list[str]


class BackendRecommender:
    """Recommends optimal backends based on circuit and system analysis."""

    def __init__(self, registry: BackendRegistry | None = None) -> None:
        self.registry = registry or BackendRegistry()

    def detect_system_capabilities(self) -> SystemCapabilities:
        """Detect current system capabilities."""
        mem = psutil.virtual_memory()

        gpu_available = False
        gpu_memory = None

        # Check for CUDA GPU
        try:
            import cupy

            gpu_available = True
            gpu_memory = cupy.cuda.Device().mem_info[1] / (1024**3)  # Total in GB
        except (ImportError, Exception):
            pass

        return SystemCapabilities(
            total_memory_gb=mem.total / (1024**3),
            available_memory_gb=mem.available / (1024**3),
            has_gpu=gpu_available,
            gpu_memory_gb=gpu_memory,
            cpu_cores=psutil.cpu_count(logical=False) or 1,
        )

    def estimate_memory_requirement(
        self, num_wires: int, is_mixed: bool = False
    ) -> float:
        """Estimate memory requirement in GB for a circuit."""
        # State vector: 2^n complex numbers (16 bytes each)
        # Density matrix: 2^(2n) complex numbers
        if is_mixed:
            elements = 2 ** (2 * num_wires)
        else:
            elements = 2**num_wires

        bytes_required = elements * 16  # complex128
        return bytes_required / (1024**3)

    def recommend(
        self,
        circuit: CircuitRepresentation,
        prefer_speed: bool = True,
        allow_cloud: bool = False,
    ) -> list[Recommendation]:
        """Generate ranked backend recommendations for a circuit."""
        specs = circuit.get_specs()
        num_wires = specs.get("num_device_wires", 2)
        system = self.detect_system_capabilities()
        memory_needed = self.estimate_memory_requirement(num_wires)

        recommendations: list[Recommendation] = []

        for status in self.registry.list_available():
            if not allow_cloud and status.info.backend_type == BackendType.CLOUD:
                continue

            score, reasons, warnings = self._score_backend(
                status, num_wires, memory_needed, system, prefer_speed
            )

            recommendations.append(
                Recommendation(
                    backend_status=status,
                    score=score,
                    reasons=reasons,
                    warnings=warnings,
                )
            )

        # Sort by score descending
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations

    def _score_backend(
        self,
        status: BackendStatus,
        num_wires: int,
        memory_needed: float,
        system: SystemCapabilities,
        prefer_speed: bool,
    ) -> tuple[float, list[str], list[str]]:
        """Score a backend for the given circuit and system."""
        score = 50.0  # Base score
        reasons: list[str] = []
        warnings: list[str] = []
        info = status.info

        # Check wire limit
        if info.max_wires and num_wires > info.max_wires:
            return 0.0, [], [f"Exceeds max wires ({info.max_wires})"]

        # Memory check
        if memory_needed > system.available_memory_gb * 0.8:
            warnings.append(f"May require {memory_needed:.1f}GB memory")
            score -= 20

        # Speed preference
        if prefer_speed:
            if info.estimated_speed == "fast":
                score += 20
                reasons.append("Fast execution")
            elif info.estimated_speed == "slow":
                score -= 10

        # GPU bonus
        if info.supports_gpu and system.has_gpu:
            score += 25
            reasons.append("GPU acceleration available")

        # Local vs cloud
        if info.backend_type == BackendType.LOCAL:
            score += 10
            reasons.append("No network latency")
        elif info.backend_type == BackendType.CLOUD:
            if info.cost_per_task:
                warnings.append(f"Cost: ${info.cost_per_task:.5f}/task")

        # Lightning bonus for medium-large circuits
        if info.backend_type == BackendType.LIGHTNING:
            if num_wires >= 10:
                score += 15
                reasons.append("Optimized for larger circuits")

        return score, reasons, warnings
