"""Unit tests for backend module (no API key required)."""

from skadi.backends.base import Backend, BackendInfo, BackendType
from skadi.backends.local import DefaultMixedBackend, DefaultQubitBackend
from skadi.backends.registry import BackendRegistry, BackendStatus


class TestBackendInfo:
    """Tests for BackendInfo dataclass."""

    def test_backend_info_creation(self) -> None:
        """Test creating a BackendInfo instance."""
        info = BackendInfo(
            name="test.backend",
            device_name="test.device",
            backend_type=BackendType.LOCAL,
            description="Test backend",
            max_wires=10,
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=False,
            estimated_speed="fast",
            cost_per_task=None,
        )

        assert info.name == "test.backend"
        assert info.backend_type == BackendType.LOCAL
        assert info.max_wires == 10
        assert info.cost_per_task is None


class TestBackendType:
    """Tests for BackendType enum."""

    def test_backend_types(self) -> None:
        """Test all backend type values."""
        assert BackendType.LOCAL.value == "local"
        assert BackendType.LIGHTNING.value == "lightning"
        assert BackendType.CLOUD.value == "cloud"


class TestDefaultQubitBackend:
    """Tests for DefaultQubitBackend."""

    def test_get_info(self) -> None:
        """Test getting backend info."""
        backend = DefaultQubitBackend()
        info = backend.get_info()

        assert info.name == "default.qubit"
        assert info.device_name == "default.qubit"
        assert info.backend_type == BackendType.LOCAL
        assert info.max_wires > 0  # Dynamically calculated from available memory
        assert info.supports_shots is True
        assert info.requires_credentials is False
        assert info.cost_per_task is None

    def test_is_available(self) -> None:
        """Test availability check."""
        backend = DefaultQubitBackend()
        assert backend.is_available() is True

    def test_get_availability_reason(self) -> None:
        """Test availability reason."""
        backend = DefaultQubitBackend()
        reason = backend.get_availability_reason()
        assert "always available" in reason.lower()

    def test_create_device(self) -> None:
        """Test device creation."""
        backend = DefaultQubitBackend()
        device = backend.create_device(wires=2)

        assert device is not None
        # PennyLane new device API uses wires property
        assert len(device.wires) == 2

    def test_create_device_with_shots(self) -> None:
        """Test device creation with shots."""
        backend = DefaultQubitBackend()
        device = backend.create_device(wires=3, shots=1000)

        assert device is not None
        assert len(device.wires) == 3


class TestDefaultMixedBackend:
    """Tests for DefaultMixedBackend."""

    def test_get_info(self) -> None:
        """Test getting backend info."""
        backend = DefaultMixedBackend()
        info = backend.get_info()

        assert info.name == "default.mixed"
        assert info.backend_type == BackendType.LOCAL
        assert info.max_wires > 0  # Dynamically calculated from available memory

    def test_is_available(self) -> None:
        """Test availability check."""
        backend = DefaultMixedBackend()
        assert backend.is_available() is True

    def test_create_device(self) -> None:
        """Test device creation."""
        backend = DefaultMixedBackend()
        device = backend.create_device(wires=2)

        assert device is not None


class TestBackendRegistry:
    """Tests for BackendRegistry."""

    def test_default_backends_registered(self) -> None:
        """Test that default backends are registered."""
        registry = BackendRegistry()
        all_backends = registry.list_all()

        # Should have at least local backends
        names = [s.info.name for s in all_backends]
        assert "default.qubit" in names
        assert "default.mixed" in names

    def test_get_backend(self) -> None:
        """Test getting a backend by name."""
        registry = BackendRegistry()

        backend = registry.get("default.qubit")
        assert backend is not None
        assert backend.get_info().name == "default.qubit"

    def test_get_nonexistent_backend(self) -> None:
        """Test getting a nonexistent backend."""
        registry = BackendRegistry()

        backend = registry.get("nonexistent.backend")
        assert backend is None

    def test_list_available(self) -> None:
        """Test listing available backends."""
        registry = BackendRegistry()
        available = registry.list_available()

        # At least local backends should be available
        assert len(available) >= 2
        for status in available:
            assert status.available is True

    def test_list_all(self) -> None:
        """Test listing all backends."""
        registry = BackendRegistry()
        all_backends = registry.list_all()

        # Should include all registered backends
        assert len(all_backends) >= 2

    def test_get_by_type(self) -> None:
        """Test filtering backends by type."""
        registry = BackendRegistry()

        local_backends = registry.get_by_type(BackendType.LOCAL)
        assert len(local_backends) >= 2

        for status in local_backends:
            assert status.info.backend_type == BackendType.LOCAL

    def test_register_custom_backend(self) -> None:
        """Test registering a custom backend."""

        class CustomBackend(Backend):
            def get_info(self) -> BackendInfo:
                return BackendInfo(
                    name="custom.test",
                    device_name="custom.test",
                    backend_type=BackendType.LOCAL,
                    description="Custom test backend",
                    max_wires=5,
                    supports_shots=True,
                    supports_gpu=False,
                    requires_credentials=False,
                    estimated_speed="fast",
                    cost_per_task=None,
                )

            def is_available(self) -> bool:
                return True

            def get_availability_reason(self) -> str:
                return "Custom backend always available"

            def create_device(self, wires: int, shots=None, **kwargs):
                import pennylane as qml

                return qml.device("default.qubit", wires=wires, shots=shots)

        registry = BackendRegistry()
        registry.register(CustomBackend())

        custom = registry.get("custom.test")
        assert custom is not None
        assert custom.get_info().name == "custom.test"


class TestBackendStatus:
    """Tests for BackendStatus dataclass."""

    def test_backend_status(self) -> None:
        """Test BackendStatus creation."""
        backend = DefaultQubitBackend()
        status = BackendStatus(
            backend=backend,
            info=backend.get_info(),
            available=True,
            availability_reason="Always available",
        )

        assert status.available is True
        assert status.info.name == "default.qubit"
