# Skadi Examples

This directory contains example scripts demonstrating how to use Skadi for generating and manipulating PennyLane quantum circuits using natural language.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your OpenRouter API key:
   ```bash
   cp ../.env.example ../.env
   # Edit .env and add your OpenRouter API key
   ```

   Get your API key from [OpenRouter](https://openrouter.ai/)

## Running Examples

### Generate Circuit Example

The `generate_circuit.py` script demonstrates circuit generation and manipulation:

```bash
python examples/generate_circuit.py
```

This example shows:
- Loading environment variables
- Initializing the circuit generator
- Generating a Bell state circuit from natural language
- Generating a superposition circuit
- Displaying the generated code and circuit output

## What to Try

Here are some natural language descriptions you can try:

- "Create a Bell state circuit"
- "Create a circuit that puts a single qubit in superposition using a Hadamard gate"
- "Create a 3-qubit GHZ state"
- "Create a quantum teleportation circuit"
- "Apply a rotation around the X axis by pi/4 radians"

## Output

The example script will:
1. Display the natural language description
2. Show the generated PennyLane code
3. Execute the circuit
4. Display the circuit output (state vector or probabilities)
5. Show the circuit structure

## Troubleshooting

If you encounter errors:

1. **API Key Error**: Make sure your `.env` file contains a valid `OPENROUTER_API_KEY`
2. **Import Errors**: Ensure you've installed the package dependencies with `uv sync`
3. **Circuit Execution Errors**: The LLM-generated code may sometimes need validation - check the generated code for syntax issues
