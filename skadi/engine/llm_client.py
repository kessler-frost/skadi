"""LLM client for natural language to PennyLane circuit generation."""

import re
from typing import Optional

from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from skadi.config import settings


class LLMClient:
    """Client for interfacing with LLM via OpenRouter."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenRouter API key. If None, uses settings.openrouter_api_key.
            model: The model to use for generation. If None, uses settings.openrouter_model.

        Raises:
            ValueError: If API key is not provided and not found in settings.
        """
        self.api_key = api_key or settings.openrouter_api_key
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable "
                "or pass api_key to LLMClient constructor."
            )

        self.model_id = model or settings.openrouter_model
        # Pass API key directly to OpenRouter instead of modifying environment
        self.agent = Agent(
            model=OpenRouter(id=self.model_id, api_key=self.api_key), markdown=False
        )

    def generate_circuit_code(
        self, description: str, knowledge_context: str = "", error_feedback: str = ""
    ) -> str:
        """
        Generate PennyLane circuit code from natural language description.

        Args:
            description: Natural language description of the quantum circuit.
            knowledge_context: Optional knowledge context to augment the prompt.
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

        # Build prompt with optional knowledge context and error feedback
        prompt_parts = [base_prompt]

        if knowledge_context:
            prompt_parts.append(
                f"""
---

**KNOWLEDGE CONTEXT:**
The following information may help you generate the circuit:

{knowledge_context}

---"""
            )

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
