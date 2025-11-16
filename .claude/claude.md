# Skadi - Quantum Circuit Generation

## Project Overview

Skadi generates PennyLane quantum circuits from natural language using LLM orchestration with dual knowledge sources for enhanced accuracy.

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
- **Testing**: Unit tests should NOT require API keys - only functional/integration tests should require `OPENROUTER_API_KEY`
- **No Fallbacks**: NEVER add try/except fallbacks or backwards compatibility code - we only support current and upcoming versions of PennyLane
- **Minimal try/except**: Keep if/else conditions and try/except blocks to an absolute minimum to avoid multiple code paths

### Project Structure

```
skadi/
├── skadi/
│   ├── core/          # Circuit generation and validation
│   ├── engine/        # LLM client and knowledge base (Agno RAG)
│   ├── knowledge/     # Dual knowledge sources (Agno KB + Context7)
│   └── utils/         # Documentation scraper (Crawl4AI)
├── tests/             # Test suite
├── examples/          # Example scripts
└── data/              # LanceDB vector storage and scraped docs
```

### Technologies

- **PennyLane**: Quantum circuit framework
- **Agno**: LLM orchestration and RAG framework
- **OpenRouter**: LLM API gateway (Claude Haiku 4.5)
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
   - LanceDB storage with OpenAI embeddings
   - Hybrid search (vector + keyword)

2. **Context7 Client** (static API docs)
   - Direct API documentation access
   - Minimal latency for common queries

Both sources are combined via `KnowledgeAugmenter` for optimal context.
