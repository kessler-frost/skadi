# Skadi

Generate and manipulate PennyLane quantum circuits using natural language.

## Setup

```bash
# Install dependencies
uv sync

# Configure API key
cp .env.example .env
# Add your OpenRouter API key to .env
```

Get an API key from [OpenRouter](https://openrouter.ai/).

## Usage

```python
from skadi import CircuitGenerator

generator = CircuitGenerator()
circuit = generator.generate("Create a Bell state circuit")
result = circuit()
print(result)
```

## Example Prompts

- "Create a Bell state circuit"
- "Create a 3-qubit GHZ state"
- "Apply a rotation around the X axis by pi/4 radians"
- "Create a quantum teleportation circuit"

## Architecture

- **LLM Client** (`skadi/engine/llm_client.py`) - OpenRouter API interface using Claude Haiku 4.5
- **Circuit Generator** (`skadi/core/circuit_generator.py`) - Code generation, validation, and execution

## Examples

```bash
uv run python examples/generate_circuit.py
```

## Development

```bash
# Run tests
uv run pytest tests/

# Run linting
uv run ruff check .
uv run ruff format .
```

## Advanced Usage

### Get both circuit and code

```python
circuit, code = generator.generate_with_code("Create a Bell state circuit")
print("Generated code:")
print(code)
print("\nResult:")
print(circuit())
```

### Error handling

```python
try:
    circuit = generator.generate("Create a quantum circuit")
    result = circuit()
except ValueError as e:
    print(f"Validation error: {e}")
```

## Troubleshooting

**API key error?** - Ensure `.env` exists with `OPENROUTER_API_KEY=your-key`

**Import errors?** - Run `uv sync`

**Generated code invalid?** - Try making your prompt more specific

## License

Apache License 2.0 - see LICENSE file for details.
