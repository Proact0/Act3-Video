# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- `uv venv` - Create virtual environment
- `uv sync --all-packages` - Install all dependencies
- `uv sync --package cast_name` - Install specific cast package

### LangGraph Development
- `uv run langgraph dev` - Start LangGraph development server
  - API: http://127.0.0.1:2024
  - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
  - API docs: http://127.0.0.1:2024/docs

### Testing
- `pytest` - Run tests (check pyproject.toml for test configuration)

### Code Quality
- `ruff check` - Run linting
- `ruff format` - Format code
- `pre-commit run --all-files` - Run all pre-commit hooks

## Architecture Overview

This is a LangGraph-based AI system template using LangChain. The project follows a modular cast-based architecture:

### Core Components

**Base Classes:**
- `casts/base_node.py` - Abstract base class for all nodes with `execute()` method
- `casts/base_workflow.py` - Abstract base class for workflows with `build()` method returning `CompiledStateGraph`

**Main Structure:**
- `casts/workflow.py` - Main workflow orchestrating all cast workflows
- `casts/state.py` - Main state definition using TypedDict with LangGraph message annotations

**Cast System:**
Each cast in `casts/{cast_name}/` contains:
- `workflow.py` - Cast-specific workflow inheriting from BaseWorkflow
- `modules/state.py` - Cast state definition using @dataclass
- `modules/` - Contains nodes, tools, prompts, models, chains, conditions, utils

### Workflow Configuration

**langgraph.json** defines available workflows:
- `main` - Main workflow entry point
- `cast_name` - Individual cast workflows

### State Management

- Main state uses TypedDict with LangGraph message annotations
- Cast states use @dataclass for type safety
- States flow through workflow nodes via the execute() method

### Key Patterns

- All nodes inherit from BaseNode and implement execute(state) -> dict
- All workflows inherit from BaseWorkflow and implement build() -> CompiledStateGraph
- Cast structure is repeatable - copy cast_name template for new casts
- Pre-commit hooks enforce code quality with ruff