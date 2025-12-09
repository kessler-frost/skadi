# Skadi

Generate, manipulate, and execute PennyLane quantum circuits using natural language.

## Demo

![Skadi Demo](demo.gif)

## Installation

```bash
# Run directly with uvx (no installation needed)
uvx --from git+https://github.com/kessler-frost/skadi skadi main "create a bell state"

# Or install/upgrade as a tool (always gets latest version)
uv tool install --reinstall git+https://github.com/kessler-frost/skadi

# Set your API key (defaults to OpenRouter)
export SKADI_API_KEY="your-key-here"
```

**Get an API key:**

- OpenRouter (default): <https://openrouter.ai/>
- Or use any OpenAI-compatible provider by setting `SKADI_BASE_URL`

## Quick Start

```bash
# Create a circuit
skadi main "create a bell state circuit"

# Modify it
skadi main "add a third qubit with hadamard"

# Optimize it
skadi main "optimize the circuit"

# Execute it
skadi run --auto

# Show current circuit
skadi main show

# Clear circuit file
skadi main clear
```

All circuits are saved to `circuit.py` and visualized as ASCII art in your terminal.

## More Examples

**Generate circuits:**

```bash
skadi main "create a 3-qubit GHZ state"
skadi main "create a quantum fourier transform for 4 qubits"
```

**Modify and optimize:**

```bash
skadi main "add a rotation gate before the CNOT"
skadi main "optimize the circuit aggressively"
```

**View and manage:**

```bash
skadi main show              # Display current circuit
skadi main show --with-code  # Show circuit with code
skadi main clear             # Remove circuit.py
```

## Execution

**Run circuits on quantum backends:**

```bash
skadi run                          # Interactive backend selection
skadi run --auto                   # Auto-select best backend
skadi run --backend default.qubit  # Use specific backend
```

**List available backends:**

```bash
skadi backends       # Show available backends
skadi backends --all # Show all backends (including unavailable)
```

Available backends include local simulators (`default.qubit`, `default.mixed`), high-performance simulators (`lightning.qubit`), and cloud backends (AWS Braket).

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
