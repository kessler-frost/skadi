"""LLM client for natural language to PennyLane circuit generation."""

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
        self, description: str, knowledge_context: str = ""
    ) -> str:
        """
        Generate PennyLane circuit code from natural language description.

        Args:
            description: Natural language description of the quantum circuit.
            knowledge_context: Optional knowledge context to augment the prompt.

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

        # If knowledge context is provided, augment the prompt
        if knowledge_context:
            prompt = f"""{base_prompt}

---

**KNOWLEDGE CONTEXT:**
The following information may help you generate the circuit:

{knowledge_context}

---

Now generate the code for: {description}"""
        else:
            prompt = f"{base_prompt}\n\nNow generate the code for: {description}"

        try:
            # Use the agent to generate the response
            response = self.agent.run(prompt)
            code = response.content.strip()

            # Remove markdown code blocks if present
            if code.startswith("```python"):
                code = code[len("```python") :].strip()
            if code.startswith("```"):
                code = code[3:].strip()
            if code.endswith("```"):
                code = code[:-3].strip()

            return code

        except Exception as e:
            raise Exception(f"Failed to generate circuit code: {str(e)}")
