"""AWS Braket cloud simulator backends."""

from typing import Any

import pennylane as qml
from pennylane.devices import Device

from skadi.backends.base import Backend, BackendInfo, BackendType
from skadi.config import settings


class BraketBackendBase(Backend):
    """Base class for AWS Braket backends."""

    def _has_braket_plugin(self) -> bool:
        try:
            from braket.pennylane_plugin import BraketAwsQubitDevice  # noqa: F401

            return True
        except ImportError:
            return False

    def _has_aws_credentials(self) -> bool:
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            return True
        try:
            import boto3

            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
        except Exception:
            return False


class BraketSV1Backend(BraketBackendBase):
    """AWS Braket SV1 state vector simulator."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="braket.sv1",
            device_name="braket.aws.qubit",
            backend_type=BackendType.CLOUD,
            description="AWS managed state vector simulator (up to 34 qubits)",
            max_wires=34,
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=True,
            estimated_speed="medium",
            cost_per_task=0.00075,
        )

    def is_available(self) -> bool:
        return self._has_braket_plugin() and self._has_aws_credentials()

    def get_availability_reason(self) -> str:
        if not self._has_braket_plugin():
            return "Install with: uv add amazon-braket-pennylane-plugin"
        if not self._has_aws_credentials():
            return "AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        return "Amazon Braket SDK and AWS credentials available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        device_arn = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
        s3_bucket = settings.aws_braket_s3_bucket
        s3_prefix = settings.aws_braket_s3_prefix

        return qml.device(
            "braket.aws.qubit",
            device_arn=device_arn,
            wires=wires,
            shots=shots or 1000,
            s3_destination_folder=(s3_bucket, s3_prefix),
            **kwargs,
        )


class BraketDM1Backend(BraketBackendBase):
    """AWS Braket DM1 density matrix simulator."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="braket.dm1",
            device_name="braket.aws.qubit",
            backend_type=BackendType.CLOUD,
            description="AWS managed density matrix simulator (up to 17 qubits)",
            max_wires=17,
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=True,
            estimated_speed="medium",
            cost_per_task=0.00075,
        )

    def is_available(self) -> bool:
        return self._has_braket_plugin() and self._has_aws_credentials()

    def get_availability_reason(self) -> str:
        if not self._has_braket_plugin():
            return "Install with: uv add amazon-braket-pennylane-plugin"
        if not self._has_aws_credentials():
            return "AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        return "Amazon Braket SDK and AWS credentials available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        device_arn = "arn:aws:braket:::device/quantum-simulator/amazon/dm1"
        s3_bucket = settings.aws_braket_s3_bucket
        s3_prefix = settings.aws_braket_s3_prefix

        return qml.device(
            "braket.aws.qubit",
            device_arn=device_arn,
            wires=wires,
            shots=shots or 1000,
            s3_destination_folder=(s3_bucket, s3_prefix),
            **kwargs,
        )


class BraketTN1Backend(BraketBackendBase):
    """AWS Braket TN1 tensor network simulator."""

    def get_info(self) -> BackendInfo:
        return BackendInfo(
            name="braket.tn1",
            device_name="braket.aws.qubit",
            backend_type=BackendType.CLOUD,
            description="AWS tensor network simulator (up to 50 qubits, limited gates)",
            max_wires=50,
            supports_shots=True,
            supports_gpu=False,
            requires_credentials=True,
            estimated_speed="slow",
            cost_per_task=0.275,
        )

    def is_available(self) -> bool:
        return self._has_braket_plugin() and self._has_aws_credentials()

    def get_availability_reason(self) -> str:
        if not self._has_braket_plugin():
            return "Install with: uv add amazon-braket-pennylane-plugin"
        if not self._has_aws_credentials():
            return "AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        return "Amazon Braket SDK and AWS credentials available"

    def create_device(
        self, wires: int, shots: int | None = None, **kwargs: Any
    ) -> Device:
        device_arn = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
        s3_bucket = settings.aws_braket_s3_bucket
        s3_prefix = settings.aws_braket_s3_prefix

        return qml.device(
            "braket.aws.qubit",
            device_arn=device_arn,
            wires=wires,
            shots=shots or 1000,
            s3_destination_folder=(s3_bucket, s3_prefix),
            **kwargs,
        )
