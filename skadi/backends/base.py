"""Base classes for quantum execution backends."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import psutil
from pennylane.devices import Device


def get_available_memory_gb() -> float:
    """Get available system memory in GB."""
    return psutil.virtual_memory().available / (1024**3)


def calculate_max_wires(is_mixed: bool = False, memory_fraction: float = 0.8) -> int:
    """Calculate maximum qubits based on available system memory.

    Args:
        is_mixed: If True, calculate for density matrix (2^2n scaling).
                  If False, calculate for state vector (2^n scaling).
        memory_fraction: Fraction of available memory to use (default 80%).

    Returns:
        Maximum number of qubits that can be simulated.
    """
    available_gb = get_available_memory_gb() * memory_fraction
    available_bytes = available_gb * (1024**3)

    # Each complex128 element is 16 bytes
    max_elements = available_bytes / 16

    # State vector: 2^n elements, Density matrix: 2^(2n) elements
    max_wires = int(math.log2(max_elements))
    if is_mixed:
        max_wires = max_wires // 2

    return max_wires


class BackendType(Enum):
    """Type of quantum backend."""

    LOCAL = "local"
    LIGHTNING = "lightning"
    CLOUD = "cloud"


@dataclass
class BackendInfo:
    """Information about an available backend."""

    name: str
    device_name: str  # e.g., "default.qubit", "lightning.qubit"
    backend_type: BackendType
    description: str
    max_wires: int | None  # None = unlimited
    supports_shots: bool
    supports_gpu: bool
    requires_credentials: bool
    estimated_speed: str  # "fast", "medium", "slow"
    cost_per_task: float | None  # None = free


class Backend(ABC):
    """Abstract base class for quantum execution backends."""

    @abstractmethod
    def get_info(self) -> BackendInfo:
        """Return information about this backend."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is currently available."""
        ...

    @abstractmethod
    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        """Create a PennyLane device for this backend."""
        ...

    @abstractmethod
    def get_availability_reason(self) -> str:
        """Explain why backend is/isn't available."""
        ...
