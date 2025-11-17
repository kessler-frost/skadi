"""LLM client for natural language to PennyLane circuit generation."""

import re
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.models.openrouter import OpenRouter

from skadi.config import settings


class LLMClient:
    """Client for interfacing with LLM providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for the provider. If None, uses settings.skadi_api_key.
            model: The model to use for generation. If None, uses settings.skadi_model.
            base_url: Base URL for custom provider. If None, uses OpenRouter.

        Raises:
            ValueError: If API key is not provided and not found in settings.
        """
        self.api_key = api_key or settings.skadi_api_key
        if not self.api_key:
            raise ValueError(
                "API key not found. Please set SKADI_API_KEY environment variable "
                "or pass api_key to LLMClient constructor."
            )

        self.model_id = model or settings.skadi_model
        self.base_url = base_url if base_url is not None else settings.skadi_base_url

        # Create agent with appropriate model based on base_url
        llm_model = self._create_model()
        self.agent = Agent(model=llm_model, markdown=False)

    def _create_model(self):
        """
        Create appropriate Agno model based on base_url.

        Returns:
            Agno model instance (OpenRouter if base_url is None, otherwise OpenAILike).
        """
        if self.base_url is None:
            # Default: Use OpenRouter
            return OpenRouter(id=self.model_id, api_key=self.api_key)
        # Custom provider: Use OpenAI-compatible API
        return OpenAILike(
            id=self.model_id, api_key=self.api_key, base_url=self.base_url
        )

    def generate_circuit_code(self, description: str, error_feedback: str = "") -> str:
        """
        Generate PennyLane circuit code from natural language description.

        Args:
            description: Natural language description of the quantum circuit.
            error_feedback: Optional error message from previous generation attempt.

        Returns:
            Python code string containing PennyLane circuit implementation.

        Raises:
            Exception: If the API call fails.
        """
        # Base prompt template
        base_prompt = """You are an expert quantum computing assistant specialized in PennyLane.
Generate valid PennyLane circuit code from this description: {description}

Guidelines:
- Generate complete, runnable Python code
- Use proper PennyLane syntax and decorators
- The function should be named 'circuit' and use @qml.qnode decorator
- Include appropriate parameters based on the description
- Add brief comments explaining the circuit structure
- Return only the Python code, no explanations
- Use 'dev = qml.device("default.qubit", wires=N)' where N is the number of qubits needed
- Ensure the circuit returns measurements using qml.state() or qml.probs()

Example format:
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    # Circuit operations here
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()"""

        # Build prompt with optional error feedback
        prompt_parts = [base_prompt]

        if error_feedback:
            prompt_parts.append(
                f"""
---

**PREVIOUS ERROR:**
The previous code generation had the following error:

{error_feedback}

Please fix this error and generate corrected code.

---"""
            )

        prompt_parts.append(f"\nNow generate the code for: {description}")
        prompt = "\n".join(prompt_parts)

        response = self.agent.run(prompt)
        code = response.content.strip()

        # Remove markdown code blocks if present
        code = re.sub(
            r"^```(?:python)?\s*|\s*```$", "", code, flags=re.MULTILINE
        ).strip()

        return code
