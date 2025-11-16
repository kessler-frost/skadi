# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a new Python project. The repository structure and tooling have not yet been established.

## Project Configuration

The project uses:
- **License**: Apache License 2.0
- **Python tooling**: Based on .gitignore, this project is configured to support modern Python package managers (uv, poetry, pdm, pixi)

## Development Workflow

### Environment Setup

When setting up the project for the first time, use `uv` for Python environment management and dependency installation (once a pyproject.toml or requirements file is added).

### Git Workflow

This is a git repository. Use standard git commands for version control:
- Check status: `git status`
- View changes: `git --no-pager diff`
- View history: `git --no-pager log --oneline`

## Notes for Future Development

As this project evolves, update this WARP.md with:
- Build commands (e.g., how to build/compile the project)
- Test commands (e.g., pytest, unittest)
- Lint/format commands (e.g., ruff, black, mypy)
- Project architecture and code organization
- Key modules and their responsibilities
- Development conventions and patterns specific to this project
