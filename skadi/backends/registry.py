"""Backend registry for discovering and managing quantum backends."""

from dataclasses import dataclass

from skadi.backends.base import Backend, BackendInfo, BackendType
from skadi.backends.braket import (
    BraketDM1Backend,
    BraketSV1Backend,
    BraketTN1Backend,
)
from skadi.backends.lightning import LightningGPUBackend, LightningQubitBackend
from skadi.backends.local import DefaultMixedBackend, DefaultQubitBackend


@dataclass
class BackendStatus:
    """Status of a registered backend."""

    backend: Backend
    info: BackendInfo
    available: bool
    availability_reason: str


class BackendRegistry:
    """Registry of all available quantum execution backends."""

    def __init__(self) -> None:
        self._backends: dict[str, Backend] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all built-in backends."""
        # Local backends (always available)
        self.register(DefaultQubitBackend())
        self.register(DefaultMixedBackend())

        # Lightning backends (optional)
        self.register(LightningQubitBackend())
        self.register(LightningGPUBackend())

        # Cloud backends (require credentials)
        self.register(BraketSV1Backend())
        self.register(BraketDM1Backend())
        self.register(BraketTN1Backend())

    def register(self, backend: Backend) -> None:
        """Register a new backend."""
        info = backend.get_info()
        self._backends[info.name] = backend

    def get(self, name: str) -> Backend | None:
        """Get a backend by name."""
        return self._backends.get(name)

    def list_all(self) -> list[BackendStatus]:
        """List all registered backends with their status."""
        return [
            BackendStatus(
                backend=backend,
                info=backend.get_info(),
                available=backend.is_available(),
                availability_reason=backend.get_availability_reason(),
            )
            for backend in self._backends.values()
        ]

    def list_available(self) -> list[BackendStatus]:
        """List only available backends."""
        return [status for status in self.list_all() if status.available]

    def get_by_type(self, backend_type: BackendType) -> list[BackendStatus]:
        """Get backends filtered by type."""
        return [
            status
            for status in self.list_all()
            if status.info.backend_type == backend_type
        ]
