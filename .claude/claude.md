# Skadi - Quantum Circuit Generation

## Project Overview

Skadi generates PennyLane quantum circuits from natural language using LLM orchestration.

## Core Design Principle

**Simplicity to the user is the highest priority.** All features, architecture decisions, and improvements should prioritize making Skadi as simple and accessible as possible for end users. When in doubt between power-user features and simplicity, choose simplicity.

## Development Guidelines

### Package Management

- **Always use `uv` for package management** (not pip, poetry, or conda)
- Add dependencies: `uv add <package>`
- Install dependencies: `uv sync`
- Run scripts: `uv run <script>`

### Code Quality

- Ruff is configured as a pre-commit hook for linting and formatting
- Run manually: `uv run ruff check .` and `uv run ruff format .`
- Keep code minimal and tidy

### Planning & Execution

- **ALWAYS use multiple agents in parallel for implementation** - this is required for all plans
- Break down complex tasks into smaller, parallelizable units
- Use TodoWrite tool to track progress on multi-step tasks

### Code Standards

- **Path Handling**: Always use `pathlib.Path` instead of `os.path.*` functions
- **Module Imports**: Avoid using `sys.path.insert()` or modifying `sys.path` - use proper package installation instead
- **Configuration**: Always use the `settings` object from `skadi.config` instead of `os.getenv()` or `os.environ`
- **Testing**: Unit tests should NOT require API keys - only functional/integration tests should require `SKADI_API_KEY`
- **No Fallbacks**: NEVER add try/except fallbacks or backwards compatibility code - we only support current and upcoming versions of PennyLane
- **Minimal try/except**: Keep if/else conditions and try/except blocks to an absolute minimum to avoid multiple code paths

### Project Structure

```bash
skadi/
├── skadi/
│   ├── core/          # Circuit generation, validation, representation, and file management
│   ├── engine/        # LLM client
│   └── manipulation/  # Circuit transformations, optimization, and analysis
├── tests/             # Test suite
└── examples/          # Example scripts
```

### Technologies

- **PennyLane**: Quantum circuit framework
- **Agno**: LLM orchestration framework
- **LLM Providers**: Supports OpenRouter (default) and custom OpenAI-compatible providers
- **Pydantic Settings**: Configuration management
- **Ruff**: Linting and formatting
- **uv**: Package manager

### CLI Architecture

The CLI component provides a natural language interface to Skadi:

- **Entry Point**: `skadi/cli.py` - Typer-based CLI with Rich terminal output
- **Command Pattern**: Single command with match/case handling:
  - `show`: Display current circuit (special keyword)
  - `clear`: Remove circuit.py (special keyword)
  - Everything else: Natural language processing (create/modify/optimize)
- **Workflow**: All commands work with a single `circuit.py` file in the current directory
- **Intent Detection**: Automatically detects create/modify/optimize operations from natural language
- **Code Generation**: LLM generates clean circuit code without print statements or example usage

## Configuration Management

Skadi uses `pydantic-settings` for configuration. All settings are loaded from environment variables or `.env` file.

### Required Settings

- `SKADI_API_KEY` - LLM provider API key (OpenRouter: <https://openrouter.ai/>, or your custom provider)

### Optional LLM Settings

- `SKADI_MODEL` - Model to use (default: `anthropic/claude-haiku-4.5`)
- `SKADI_BASE_URL` - Base URL for custom provider (if not set, uses OpenRouter)

See `.env.example` for all available configuration options with descriptions.

### Using Settings in Code

```python
from skadi import settings

# Access configuration values
print(f"Using model: {settings.skadi_model}")
print(f"Using base URL: {settings.skadi_base_url or 'OpenRouter (default)'}")

# Create custom settings instance
from skadi import Settings

custom_settings = Settings(
    skadi_api_key="your-key",
    skadi_model="anthropic/claude-sonnet-3.5",
    skadi_base_url=None,  # None = OpenRouter, or set to custom URL
)
```

## Advanced Usage Patterns

### Circuit Manipulation Workflow

```python
from skadi import CircuitGenerator, CircuitManipulator

generator = CircuitGenerator()
manipulator = CircuitManipulator()

# Generate circuit with metadata
circuit = generator.generate_circuit("Create a quantum Fourier transform for 3 qubits")

# Optimization with different levels
basic = manipulator.optimize(circuit, level="basic", num_passes=1)
default = manipulator.optimize(circuit, level="default", num_passes=2)
aggressive = manipulator.optimize(circuit, level="aggressive", num_passes=3)

# Analysis and explanation
analysis = manipulator.understand(circuit, include_explanation=True, verbose=True)
print(f"Complexity: {analysis['complexity']['level']}")
print(f"Explanation: {analysis['explanation']}")

# Circuit comparison
comparison = manipulator.compare_circuits(circuit, optimized, names=("Original", "Optimized"))

# Natural language rewriting
modified = manipulator.rewrite(circuit, "Add a rotation gate before the CNOT")

# Get optimization report
report = manipulator.get_optimization_report(circuit)
```

### CircuitRepresentation Usage

```python
# Generate with full metadata
circuit = generator.generate_circuit("Create a GHZ state")

# Access properties
print(circuit.description)        # Original natural language description
print(circuit.code)                # Generated Python code
print(circuit.qnode)               # Executable PennyLane QNode
print(circuit.metadata)            # Generation metadata
print(circuit.transform_history)   # List of applied transformations

# Get circuit information
specs = circuit.get_specs()                    # Circuit specifications (cached)
resources = circuit.get_resource_summary()     # Gate counts, depth, wires
visualization = circuit.get_visualization()    # Text-based circuit diagram

# Clone for experimentation
circuit_copy = circuit.clone()
circuit_with_changes = circuit.clone(description="Modified version")
```
