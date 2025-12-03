"""Lightning simulator backends for PennyLane."""

from typing import Any

import pennylane as qml
from pennylane.devices import Device

from skadi.backends.base import Backend, BackendInfo, BackendType


class LightningQubitBackend(Backend):
    """PennyLane-Lightning CPU backend."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="lightning.qubit",
            device_name="lightning.qubit",
            backend_type=BackendType.LIGHTNING,
            description="High-performance C++ state-vector simulator",
            max_wires=30,
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=False,
            estimated_speed="fast",
            cost_per_task=None,
        )

    def is_available(self) -> bool:
        try:
            import pennylane_lightning  # noqa: F401

            return True
        except ImportError:
            return False

    def get_availability_reason(self) -> str:
        if self.is_available():
            return "pennylane-lightning is installed"
        return "Install with: uv add pennylane-lightning"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        return qml.device("lightning.qubit", wires=wires, shots=shots, **kwargs)


class LightningGPUBackend(Backend):
    """PennyLane-Lightning GPU backend."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="lightning.gpu",
            device_name="lightning.gpu",
            backend_type=BackendType.LIGHTNING,
            description="CUDA-accelerated state-vector simulator",
            max_wires=32,
            supports_shots=True,
            supports_gpu=True,
            requires_credentials=False,
            estimated_speed="fast",
            cost_per_task=None,
        )

    def is_available(self) -> bool:
        try:
            import pennylane_lightning_gpu  # noqa: F401
            import cupy  # noqa: F401

            return True
        except ImportError:
            return False

    def get_availability_reason(self) -> str:
        try:
            import pennylane_lightning_gpu  # noqa: F401
        except ImportError:
            return "Install with: uv add pennylane-lightning-gpu (requires CUDA)"
        try:
            import cupy  # noqa: F401
        except ImportError:
            return "CUDA not available or cupy not installed"
        return "pennylane-lightning-gpu and CUDA are available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        return qml.device("lightning.gpu", wires=wires, shots=shots, **kwargs)
