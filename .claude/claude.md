# Skadi - Quantum Circuit Generation and Manipulation

## Project Overview

Skadi is a quantum circuit generation and manipulation tool that enables natural language-based operations on quantum circuits using PennyLane and Claude AI via OpenRouter.

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

- **ALWAYS use multiple agents in parallel for implementation** - this is required for all plans and put it in the plan on how you'll do it
- Break down complex tasks into smaller, parallelizable units
- Use TodoWrite tool to track progress on multi-step tasks

### Project Structure

```
skadi/
├── skadi/              # Main package
│   ├── core/          # Core circuit generation and manipulation logic
│   ├── engine/        # LLM client for natural language processing
│   └── utils/         # Utilities and helpers
├── tests/             # Test suite
├── examples/          # Example scripts
├── .claude/           # Claude Code configuration
└── pyproject.toml     # Project dependencies (managed by uv)
```

### Key Features

1. **Circuit Generation**: Create PennyLane circuits from natural language descriptions
2. **Circuit Manipulation**: Merge, transform, optimize, and modify quantum circuits (planned)
3. **Circuit Analysis**: Understand structure and reverse engineer circuits (planned)
4. **Natural Language Interface**: Powered by Claude Haiku 4.5 via OpenRouter
5. **Code Validation**: Automatic validation of generated PennyLane code
6. **Local Execution**: Run circuits on local quantum simulators

### Technologies

- **PennyLane**: Quantum circuit framework
- **Agno**: LLM orchestration framework
- **OpenRouter**: API gateway for Claude AI
- **Ruff**: Linting and formatting
- **uv**: Fast Python package manager
