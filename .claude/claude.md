# Skadi - Quantum Circuit Generation

## Project Overview

Skadi generates PennyLane quantum circuits from natural language using LLM orchestration with dual knowledge sources for enhanced accuracy.

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

```
skadi/
├── skadi/
│   ├── core/          # Circuit generation, validation, and file management
│   ├── engine/        # LLM client and knowledge base (Agno RAG)
│   ├── knowledge/     # Dual knowledge sources (Agno KB + Context7)
│   ├── manipulation/  # Circuit transformations, optimization, and analysis
│   └── utils/         # Documentation scraper (Crawl4AI)
├── tests/             # Test suite
├── examples/          # Example scripts
└── data/              # LanceDB vector storage and scraped docs
```

### Technologies

- **PennyLane**: Quantum circuit framework
- **Agno**: LLM orchestration and RAG framework
- **LLM Providers**: Supports OpenRouter (default) and custom OpenAI-compatible providers
- **LanceDB**: Vector database for embeddings
- **Context7**: Static API documentation knowledge base
- **Crawl4AI**: Documentation scraping
- **Pydantic Settings**: Configuration management
- **Ruff**: Linting and formatting
- **uv**: Package manager

### Knowledge Architecture

Dual knowledge sources enhance circuit generation:

1. **Agno Knowledge Base** (dynamic RAG)
   - Vector similarity search over scraped PennyLane docs
   - LanceDB storage with FastEmbed embeddings (open-source, local, no API key)
   - Hybrid search (vector + keyword)

2. **Context7 Client** (static API docs)
   - Direct API documentation access
   - Minimal latency for common queries

Both sources are combined via `KnowledgeAugmenter` for optimal context.

### CLI Architecture

The CLI component provides a natural language interface to Skadi:

- **Entry Point**: `skadi/cli.py` - Typer-based CLI with Rich terminal output
- **Circuit File Manager**: `skadi/core/circuit_file_manager.py` - Handles save/load of circuit.py
- **Visualizer**: `skadi/core/visualizer.py` - Uses PennyLane's qml.draw() for ASCII diagrams
- **Workflow**: All commands work with a single `circuit.py` file in the current directory
- **Intent Detection**: Automatically detects create/modify/optimize/show operations from natural language

## Configuration Management

Skadi uses `pydantic-settings` for configuration. All settings are loaded from environment variables or `.env` file.

### Required Settings

- `SKADI_API_KEY` - LLM provider API key (OpenRouter: https://openrouter.ai/, or your custom provider)

### Optional LLM Settings

- `SKADI_MODEL` - Model to use (default: `anthropic/claude-haiku-4.5`)
- `SKADI_BASE_URL` - Base URL for custom provider (if not set, uses OpenRouter)

### Optional Knowledge Base Settings

- `USE_KNOWLEDGE` - Enable knowledge augmentation (default: `true`)
- `USE_PENNYLANE_KB` - Enable PennyLane knowledge base (default: `true`)
- `USE_CONTEXT7` - Enable Context7 integration (default: `true`)
- `MAX_KNOWLEDGE_TOKENS` - Maximum tokens for knowledge retrieval (default: `2000`)
- `EMBEDDING_MODEL` - FastEmbed model for local embeddings (default: `BAAI/bge-small-en-v1.5`, ~69 MB, no API key required)

See `.env.example` for all available configuration options with descriptions.

### Using Settings in Code

```python
from skadi import settings

# Access configuration values
print(f"Using model: {settings.skadi_model}")
print(f"Using base URL: {settings.skadi_base_url or 'OpenRouter (default)'}")
print(f"Knowledge enabled: {settings.use_knowledge}")

# Create custom settings instance
from skadi import Settings

custom_settings = Settings(
    skadi_api_key="your-key",
    skadi_model="anthropic/claude-sonnet-3.5",
    skadi_base_url=None,  # None = OpenRouter, or set to custom URL
    use_knowledge=False
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

### Knowledge Base Integration

```python
from skadi import CircuitGenerator

# Option 1: Use Context7 (MCP-based, works in Claude Code)
generator = CircuitGenerator(
    use_knowledge=True,
    use_context7=True,
    use_pennylane_kb=False
)

# Option 2: Use PennyLane KB (requires scraped docs, no API key needed)
generator = CircuitGenerator(
    use_knowledge=True,
    use_context7=False,
    use_pennylane_kb=True
)

# Option 3: Use both (recommended for best results)
generator = CircuitGenerator(
    use_knowledge=True,
    use_context7=True,
    use_pennylane_kb=True
)

# Debug knowledge retrieval
stats = generator.get_knowledge_stats("bell state")
print(f"Context7 docs: {stats['context7_docs']}")
print(f"PennyLane KB results: {stats['pennylane_kb_results']}")
```
