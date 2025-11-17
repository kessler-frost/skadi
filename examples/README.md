# Skadi Examples

This directory contains example scripts demonstrating various features of Skadi.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your API keys:
   ```bash
   cp ../.env.example ../.env
   # Edit .env and add your API keys
   ```

   - `OPENROUTER_API_KEY` - Required for circuit generation (get from [OpenRouter](https://openrouter.ai/))
   - `OPENAI_API_KEY` - Required for knowledge base features (get from [OpenAI](https://platform.openai.com/))

## Examples Overview

### Basic Circuit Generation

#### `generate_circuit.py` ✅

Demonstrates basic circuit generation from natural language.

```bash
uv run python examples/generate_circuit.py
```

**Features:**
- Initialize CircuitGenerator
- Generate Bell state and superposition circuits
- View generated code and circuit output

**Requirements:** `OPENROUTER_API_KEY`

#### `circuit_manipulation_demo.py` ✅

Comprehensive demonstration of circuit manipulation features.

```bash
uv run python examples/circuit_manipulation_demo.py
```

**Features:**
- Transform: Apply PennyLane transforms (cancel_inverses, merge_rotations, etc.)
- Optimize: Reduce gate count and depth with different optimization levels
- Understand: Analyze and explain circuit structure
- Rewrite: Modify circuits with natural language
- Complete workflows: Chain operations for complex manipulations

**Requirements:** `OPENROUTER_API_KEY`

### Knowledge System

#### `use_knowledge_base.py` ⚠️ (Optional - Advanced Setup)

Shows how to use the PennyLane knowledge base for RAG.

```bash
uv run python examples/use_knowledge_base.py
```

**Features:**
- Initialize knowledge base
- Add text content and files
- Search for information
- Integrate with Agno agents

**Requirements:**
- `OPENAI_API_KEY` (for embeddings)
- **Note:** This is optional - Skadi works great with Context7 alone!
- **Future:** We plan to switch to open-source embedding solutions

#### `enhanced_generation_demo.py` ✅

Demonstrates the dual knowledge system (PennyLane KB + Context7).

```bash
uv run python examples/enhanced_generation_demo.py
```

**Features:**
- Dual knowledge system (conceptual + API docs)
- Knowledge-augmented circuit generation
- Comparison with/without knowledge

**Requirements:** `OPENROUTER_API_KEY`

### Documentation Tools

#### `scrape_docs.py` ⚠️ (Optional - Advanced Setup)

Scrapes PennyLane documentation for the knowledge base.

**Setup Required:**
```bash
# Install Playwright browsers
playwright install
```

**Run:**
```bash
uv run python examples/scrape_docs.py
```

**Features:**
- Crawl docs.pennylane.ai
- Extract and chunk text for RAG
- Save chunks with metadata
- Display statistics

**Output:** Saves to `data/pennylane_docs/`

**Note:** This is optional - only needed if you want to build the local PennyLane knowledge base

### Context7 MCP Integration

#### `context7_mcp_demo.py` ✅

Demonstrates Context7 client API (simulation mode).

```bash
PYTHONPATH=. uv run python examples/context7_mcp_demo.py
```

**Features:**
- Cache management
- Code snippet extraction
- Formatted context generation
- Convenience methods

**Note:** Uses simulated data. Real MCP calls require Claude Code environment.

#### `context7_live_mcp_example.py` ⚠️

Shows real Context7 MCP workflow (requires Claude Code).

```bash
PYTHONPATH=. uv run python examples/context7_live_mcp_example.py
```

**Requirements:** Claude Code environment with MCP access

## Quick Reference Table

| Example | Purpose | Requirements | Status |
|---------|---------|--------------|--------|
| `generate_circuit.py` | Basic circuit generation | OPENROUTER_API_KEY | ✅ |
| `circuit_manipulation_demo.py` | Circuit manipulation features | OPENROUTER_API_KEY | ✅ |
| `use_knowledge_base.py` | Knowledge base demo | OPENAI_API_KEY | ⚠️ Optional |
| `enhanced_generation_demo.py` | Dual knowledge system | OPENROUTER_API_KEY | ✅ |
| `scrape_docs.py` | Documentation scraping | playwright install | ⚠️ Optional |
| `context7_mcp_demo.py` | Context7 API demo | None | ✅ |
| `context7_live_mcp_example.py` | Live MCP usage | Claude Code env | ⚠️ Optional |

## Natural Language Prompts to Try

- "Create a Bell state circuit"
- "Create a circuit that puts a single qubit in superposition using a Hadamard gate"
- "Create a 3-qubit GHZ state"
- "Create a quantum teleportation circuit"
- "Apply a rotation around the X axis by pi/4 radians"
- "Create a Grover diffusion operator for 3 qubits"

## Troubleshooting

**API Key Errors:**
- Ensure `.env` file exists with required keys
- Copy from `.env.example`: `cp ../.env.example ../.env`

**Import Errors:**
- Run `uv sync` to install dependencies
- Use `PYTHONPATH=.` prefix when needed

**Knowledge Base Errors:**
- `OPENAI_API_KEY` required for embeddings
- First run initializes the database (may take time)

**Generated Code Issues:**
- LLM may occasionally generate invalid code
- Knowledge augmentation improves accuracy
