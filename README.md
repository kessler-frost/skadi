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

## Configuration

Skadi uses `pydantic-settings` for configuration management. All settings are loaded from environment variables or a `.env` file.

### Required Settings

- `OPENROUTER_API_KEY` - Your OpenRouter API key (get from https://openrouter.ai/)

### Optional Settings

- `OPENROUTER_MODEL` - Model to use (default: `anthropic/claude-haiku-4.5`)
- `OPENAI_API_KEY` - OpenAI API key for embeddings (required for knowledge base features)
- `USE_KNOWLEDGE` - Enable knowledge augmentation (default: `true`)
- `USE_PENNYLANE_KB` - Enable PennyLane knowledge base (default: `true`)
- `USE_CONTEXT7` - Enable Context7 integration (default: `true`)
- `MAX_KNOWLEDGE_TOKENS` - Maximum tokens for knowledge retrieval (default: `2000`)

See `.env.example` for all available configuration options with descriptions.

### Using Settings in Code

```python
from skadi import settings

# Access configuration values
print(f"Using model: {settings.openrouter_model}")
print(f"Knowledge enabled: {settings.use_knowledge}")

# Create custom settings instance
from skadi import Settings

custom_settings = Settings(
    openrouter_api_key="your-key",
    openrouter_model="anthropic/claude-sonnet-3.5",
    use_knowledge=False
)
```

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

### Core Components

- **LLM Client** (`skadi/engine/llm_client.py`) - OpenRouter API interface using Claude Haiku 4.5
- **Circuit Generator** (`skadi/core/circuit_generator.py`) - Code generation, validation, and execution

### Knowledge System

Skadi uses a dual knowledge system for enhanced circuit generation:

1. **PennyLane Knowledge Base** (`skadi/knowledge/pennylane_kb.py`)
   - Vector-based semantic search using LanceDB
   - Stores conceptual quantum computing knowledge
   - Provides understanding of algorithms and patterns
   - Requires `OPENAI_API_KEY` for embeddings

2. **Context7 Client** (`skadi/knowledge/context7_client.py`)
   - Dynamic PennyLane API documentation via MCP
   - Fetches up-to-date syntax and examples
   - Caches results to minimize API calls
   - Works in Claude Code environment

3. **Knowledge Augmenter** (`skadi/knowledge/augmenter.py`)
   - Combines both knowledge sources
   - Enriches prompts with relevant context
   - Configurable via settings

## Knowledge Base Setup

### Option 1: Using Context7 (Recommended)

Context7 provides dynamic access to PennyLane documentation via MCP (requires Claude Code environment):

```python
from skadi import CircuitGenerator

# Knowledge augmentation is enabled by default
generator = CircuitGenerator()
circuit = generator.generate("Create a Bell state circuit")
```

### Option 2: Using PennyLane Knowledge Base

For conceptual understanding and algorithm patterns:

```bash
# 1. Scrape PennyLane documentation
uv run python examples/scrape_docs.py

# 2. Use knowledge-augmented generation
uv run python examples/use_knowledge_base.py
```

Requires `OPENAI_API_KEY` for embeddings.

### Dual Knowledge System

Combine both for best results:

```python
from skadi import CircuitGenerator

generator = CircuitGenerator(
    use_knowledge=True,       # Enable knowledge augmentation
    use_pennylane_kb=True,    # Use PennyLane KB for concepts
    use_context7=True,        # Use Context7 for API docs
)
```

See `examples/enhanced_generation_demo.py` for a full demonstration.

## Examples

All examples are documented in [`examples/README.md`](examples/README.md):

```bash
# Basic circuit generation
uv run python examples/generate_circuit.py

# Knowledge base demo
uv run python examples/use_knowledge_base.py

# Enhanced generation with dual knowledge
uv run python examples/enhanced_generation_demo.py

# Documentation scraping
uv run python examples/scrape_docs.py

# Context7 MCP demos
PYTHONPATH=. uv run python examples/context7_mcp_demo.py
PYTHONPATH=. uv run python examples/context7_live_mcp_example.py
```

See [docs/CONTEXT7_MCP_INTEGRATION.md](docs/CONTEXT7_MCP_INTEGRATION.md) for detailed documentation on the Context7 MCP integration.

## Development

```bash
# Run tests
uv run pytest tests/

# Run linting
uv run ruff check .
uv run ruff format .
```

## Circuit Manipulation

Skadi provides powerful circuit manipulation capabilities for transforming, optimizing, analyzing, and rewriting quantum circuits.

### Quick Start

```python
from skadi import CircuitGenerator, CircuitManipulator

# Generate a circuit
generator = CircuitGenerator()
circuit = generator.generate_circuit("Create a Bell state with redundant gates")

# Manipulate the circuit
manipulator = CircuitManipulator()

# Transform: Apply PennyLane transforms
optimized = manipulator.optimize(circuit, level="aggressive")

# Analyze: Get circuit insights
analysis = manipulator.understand(circuit)
print(analysis["explanation"])

# Rewrite: Modify with natural language
modified = manipulator.rewrite(circuit, "Add a phase gate before CNOT")
```

### Core Operations

#### 1. **Transform** - Apply PennyLane Transforms

```python
manipulator = CircuitManipulator()

# Apply single transform
transformed = manipulator.transform(circuit, "cancel_inverses")

# Apply sequence of transforms
transforms_seq = [
    ("cancel_inverses", None),
    ("merge_rotations", None),
    ("commute_controlled", None),
]
result = manipulator.transform_sequence(circuit, transforms_seq)

# List available transforms
print(manipulator.list_transforms())
```

Available transforms: `cancel_inverses`, `merge_rotations`, `commute_controlled`, `simplify`, `adjoint`, `decompose`, `transpile`

#### 2. **Optimize** - Reduce Gate Count and Depth

```python
# Optimization levels: basic, default, aggressive
optimized = manipulator.optimize(circuit, level="aggressive", num_passes=3)

# Get optimization report
report = manipulator.get_optimization_report(optimized)
print(report["summary"])
# Output: "Applied 1 optimization(s). Reduced operations by 3. Reduced depth by 1..."

# Compare optimization levels
results = manipulator.compare_levels(circuit)
for level, circuit in results.items():
    print(f"{level}: {circuit.get_resource_summary()['num_operations']} ops")
```

#### 3. **Understand** - Analyze and Explain Circuits

```python
# Generate comprehensive analysis
analysis = manipulator.understand(circuit, include_explanation=True, verbose=True)

print(f"Complexity: {analysis['complexity']['level']}")
print(f"Operations: {analysis['specs']['num_operations']}")
print(f"Depth: {analysis['specs']['depth']}")
print(f"Entangling gates: {analysis['complexity']['entangling_gates']}")
print(f"\nExplanation:\n{analysis['explanation']}")

# Compare two circuits
comparison = manipulator.compare_circuits(original, optimized, names=("Original", "Optimized"))
print(f"Operations reduced: {comparison['differences']['operations']}")
```

#### 4. **Rewrite** - Modify with Natural Language

```python
# Modify circuit using natural language
modified = manipulator.rewrite(
    circuit,
    "Add a rotation before the CNOT gate"
)

# Simplify circuit while maintaining functionality
simplified = manipulator.simplify(circuit)
```

### Circuit Representation

All manipulation operations work with `CircuitRepresentation` objects that track metadata and transformation history:

```python
# Generate circuit with metadata
circuit = generator.generate_circuit("Create a GHZ state")

# Access circuit properties
print(circuit.description)
print(circuit.code)
print(circuit.get_resource_summary())
print(circuit.get_visualization())

# View transformation history
print(circuit.transform_history)  # List of all applied transformations

# Clone circuit for experimentation
circuit_copy = circuit.clone()
```

### Complete Workflow Example

```python
from skadi import CircuitGenerator, CircuitManipulator

# Initialize
generator = CircuitGenerator()
manipulator = CircuitManipulator()

# 1. Generate
circuit = generator.generate_circuit("Create a quantum Fourier transform for 3 qubits")
print(f"Original: {circuit.get_resource_summary()}")

# 2. Analyze
analysis = manipulator.understand(circuit)
print(f"Complexity: {analysis['complexity']['level']}")

# 3. Optimize
optimized = manipulator.optimize(circuit, level="aggressive", num_passes=2)
print(f"Optimized: {optimized.get_resource_summary()}")

# 4. Compare
comparison = manipulator.compare_circuits(circuit, optimized)
print(f"Improvement: {comparison['differences']}")

# 5. Visualize
print("\nOptimized Circuit:")
print(optimized.get_visualization())
```

### Example Script

Run the comprehensive manipulation demo:

```bash
uv run python examples/circuit_manipulation_demo.py
```

This demonstrates all four core operations (transform, optimize, understand, rewrite) with various examples.

## Advanced Usage

### Get both circuit and code

```python
circuit, code = generator.generate_with_code("Create a Bell state circuit")
print("Generated code:")
print(code)
print("\nResult:")
print(circuit())
```

### Using CircuitRepresentation directly

```python
# Generate with metadata
circuit = generator.generate_circuit("Create a Bell state")

# Access properties
specs = circuit.get_specs()
resources = circuit.get_resource_summary()
visualization = circuit.get_visualization()

# Track transformations
print(f"Applied {len(circuit.transform_history)} transformations")
```

## Troubleshooting

**API key error?** - Ensure `.env` exists with `OPENROUTER_API_KEY=your-key`

**Import errors?** - Run `uv sync`

**Generated code invalid?** - Try making your prompt more specific

## License

Apache License 2.0 - see LICENSE file for details.
