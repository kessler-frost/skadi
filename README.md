# Skadi

Generate and manipulate PennyLane quantum circuits using natural language.

## Installation

```bash
# Run directly with uvx (no installation needed)
uvx --from git+https://github.com/kessler-frost/skadi skadi "create a bell state"

# Or install as a tool
uv tool install git+https://github.com/kessler-frost/skadi

# Set your API key
export OPENROUTER_API_KEY="your-key-here"
```

Get an API key from https://openrouter.ai/

## Quick Start

```bash
# Create a circuit
skadi "create a bell state circuit"

# Modify it
skadi "add a third qubit with hadamard"

# Optimize it
skadi "optimize the circuit"

# Show current circuit
skadi "show"
```

All circuits are saved to `circuit.py` and visualized as ASCII art in your terminal.

## More Examples

**Generate circuits:**
```bash
skadi "create a 3-qubit GHZ state"
skadi "create a quantum fourier transform for 4 qubits"
```

**Modify and optimize:**
```bash
skadi "add a rotation gate before the CNOT"
skadi "optimize the circuit aggressively"
```

## Python API

```python
from skadi import CircuitGenerator, CircuitManipulator

generator = CircuitGenerator()
manipulator = CircuitManipulator()

# Generate
circuit = generator.generate_circuit("Create a Bell state")

# Optimize
optimized = manipulator.optimize(circuit, level="aggressive")

# Analyze
analysis = manipulator.understand(circuit, include_explanation=True)

# Rewrite
modified = manipulator.rewrite(circuit, "Add a phase gate before CNOT")
```

## Development

**Install locally for development:**

```bash
# Clone the repository
git clone https://github.com/kessler-frost/skadi
cd skadi

# Install as editable tool
uv tool install --editable .

# Or use within the project
uv sync
```

**Run tests and linting:**

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## License

Apache License 2.0 - see LICENSE file for details.
