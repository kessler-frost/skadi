"""Base classes for quantum execution backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pennylane.devices import Device


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
