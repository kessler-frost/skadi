"""Skadi - Generate and manipulate quantum circuits using natural language."""

from skadi.backends import BackendRecommender, BackendRegistry, CircuitExecutor
from skadi.config import Settings, settings
from skadi.core.circuit_generator import CircuitGenerator
from skadi.core.circuit_manipulator import CircuitManipulator
from skadi.core.circuit_representation import CircuitRepresentation
from skadi.engine.llm_client import LLMClient

__version__ = "0.1.0"

__all__ = [
    "BackendRecommender",
    "BackendRegistry",
    "CircuitExecutor",
    "CircuitGenerator",
    "CircuitManipulator",
    "CircuitRepresentation",
    "LLMClient",
    "Settings",
    "settings",
]
