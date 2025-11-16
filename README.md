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
