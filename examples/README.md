# Skadi Examples

This directory contains example scripts demonstrating various features of Skadi.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your API key:
   ```bash
   cp ../.env.example ../.env
   # Edit .env and add your API key
   ```

   - `SKADI_API_KEY` - Required for circuit generation (get from [OpenRouter](https://openrouter.ai/))

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

**Requirements:** `SKADI_API_KEY`

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

**Requirements:** `SKADI_API_KEY`

## Quick Reference Table

| Example | Purpose | Requirements | Status |
|---------|---------|--------------|--------|
| `generate_circuit.py` | Basic circuit generation | SKADI_API_KEY | ✅ |
| `circuit_manipulation_demo.py` | Circuit manipulation features | SKADI_API_KEY | ✅ |

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

**Generated Code Issues:**
- LLM may occasionally generate invalid code
- Retry generation or provide more specific description
