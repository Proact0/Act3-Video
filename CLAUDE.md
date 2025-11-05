# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- `uv venv` - Create virtual environment
- `uv sync --all-packages` - Install all dependencies
- `uv sync --package cast_name` - Install specific cast package (e.g., `uv sync --package cast_name`)
- `uv run pre-commit install` - Install pre-commit hooks (required for first-time setup)

### LangGraph Development
- `uv run langgraph dev` - Start LangGraph development server
  - API: http://127.0.0.1:2024
  - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
  - API docs: http://127.0.0.1:2024/docs

### Testing
- `pytest` - Run all tests
- `pytest tests/unit_tests` - Run unit tests only
- `pytest tests/integration_tests` - Run integration tests only
- `pytest tests/unit_tests/test_node.py` - Run specific test file
- `pytest -k test_function_name` - Run specific test by name

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
- `workflow.py` - Cast-specific workflow inheriting from BaseWorkflow; must export a workflow instance (e.g., `cast_name_workflow = CastNameWorkflow()`)
- `modules/state.py` - Cast state definition using @dataclass
- `modules/` - Contains nodes, tools, prompts, models, chains, conditions, utils
  - `nodes.py` - Node implementations inheriting from BaseNode
  - `tools.py` - LangChain tools for agent use
  - `prompts.py` - Prompt templates
  - `models.py` - LLM model configurations
  - `chains.py` - LangChain chain compositions
  - `conditions.py` - Conditional routing functions for workflows
  - `utils.py` - Utility functions

### Workflow Configuration

**langgraph.json** defines available workflows for the LangGraph dev server:
- `main` - Main workflow entry point (maps to `casts/workflow.py:main_workflow`)
- `cast_name` - Individual cast workflows (maps to `casts/cast_name/workflow.py:cast_name_workflow`)
- When adding new casts, add a new entry to the `graphs` section pointing to the exported workflow instance
- When installing only specific packages with `uv sync --package`, update langgraph.json to include only those workflows

### State Management

- Main state uses TypedDict with LangGraph message annotations
- Cast states use @dataclass for type safety
- States flow through workflow nodes via the execute() method

### Key Patterns

- All nodes inherit from BaseNode and implement `execute(state) -> dict`
- All workflows inherit from BaseWorkflow and implement `build() -> CompiledStateGraph`
- Workflow files must export an instance at the module level (e.g., `main_workflow = MainWorkflow(MainState)`)
- Cast structure is repeatable - copy `casts/cast_name` directory as a template for new casts
- Pre-commit hooks enforce code quality with ruff (automatically runs on git commit)
- Integration tests use `@pytest.mark.asyncio` and LangSmith's `@unit` decorator for tracking