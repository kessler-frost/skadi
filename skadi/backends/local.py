"""Local simulator backends for PennyLane."""

from typing import Any

import pennylane as qml
from pennylane.devices import Device

from skadi.backends.base import Backend, BackendInfo, BackendType, calculate_max_wires


class DefaultQubitBackend(Backend):
    """PennyLane default.qubit backend - pure state simulator."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="default.qubit",
            device_name="default.qubit",
            backend_type=BackendType.LOCAL,
            description="CPU-based pure state simulator (ideal for small circuits)",
            max_wires=calculate_max_wires(is_mixed=False),
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=False,
            estimated_speed="fast",
            cost_per_task=None,
        )

    def is_available(self) -> bool:
        return True  # Always available

    def get_availability_reason(self) -> str:
        return "Built-in PennyLane backend, always available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        return qml.device("default.qubit", wires=wires, shots=shots, **kwargs)


class DefaultMixedBackend(Backend):
    """PennyLane default.mixed backend - density matrix simulator."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="default.mixed",
            device_name="default.mixed",
            backend_type=BackendType.LOCAL,
            description="Density matrix simulator (supports noise models)",
            max_wires=calculate_max_wires(is_mixed=True),
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=False,
            estimated_speed="medium",
            cost_per_task=None,
        )

    def is_available(self) -> bool:
        return True

    def get_availability_reason(self) -> str:
        return "Built-in PennyLane backend, always available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        return qml.device("default.mixed", wires=wires, shots=shots, **kwargs)
