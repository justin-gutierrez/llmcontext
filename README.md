# LLMContext

A universal sidecar service + CLI tool that detects frameworks/libraries in a developer's codebase, collects and compresses their documentation using an LLM, tags and embeds the results, and serves optimized, RAG-ready context to agents or users via local API, file cache, or CLI.

## Features

- **Framework Detection**: Automatically detects frameworks and libraries in codebases
- **Documentation Collection**: Gathers and compresses documentation using LLM processing
- **Smart Tagging**: Tags and embeds results for optimal retrieval
- **Multiple Interfaces**: Provides CLI, API, and file cache access to optimized context

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd llmcontext

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Basic usage
llmcontext --help

# Initialize a new project
llmcontext init

# Add frameworks to track
llmcontext add react
llmcontext add tailwind --version 3.3.0
llmcontext add prisma

# List configured tools
llmcontext list-tools

# Remove a tool
llmcontext remove react

# Detect frameworks in codebase
llmcontext detect

# Start the sidecar server
llmcontext server

# Process a codebase
llmcontext process /path/to/codebase
```

### API Server

```bash
# Start the FastAPI server
llmcontext server

# Or run directly with uvicorn
uvicorn llmcontext.api:app --reload
```

The API will be available at `http://localhost:8000`

## Development

```bash
# Run tests
pytest

# Format code
black llmcontext/
isort llmcontext/

# Type checking
mypy llmcontext/

# Linting
flake8 llmcontext/
```

## Configuration

LLMContext uses a `.llmcontext.json` configuration file to manage project settings and framework tracking.

### Initializing a Project

```bash
# Create a new configuration file
llmcontext init

# Force overwrite existing config
llmcontext init --force
```

### Managing Frameworks

```bash
# Add frameworks to track
llmcontext add react
llmcontext add tailwind --version 3.3.0
llmcontext add prisma

# List configured frameworks
llmcontext list-tools

# Remove a framework
llmcontext remove react
```

### Configuration File Structure

```json
{
  "version": "1.0.0",
  "project": {
    "name": "my-project",
    "description": "",
    "frameworks": [],
    "documentation_dir": "docs",
    "cache_dir": ".llmcontext_cache"
  },
  "settings": {
    "auto_detect": true,
    "include_dev_dependencies": false,
    "compression_level": "medium",
    "embedding_model": "default",
    "max_context_length": 4000
  },
  "api": {
    "host": "127.0.0.1",
    "port": 8000,
    "enable_cors": true,
    "rate_limit": 100
  },
  "tools": {
    "enabled": ["react", "tailwind"],
    "tool_configs": {
      "react": {
        "version": "18.2.0",
        "detection_patterns": ["package.json", "src/**/*.jsx"],
        "documentation_sources": ["https://react.dev"],
        "priority": "normal"
      }
    }
  }
}
```

## Project Structure

```
llmcontext/
├── llmcontext/
│   ├── __init__.py
│   ├── cli/             # CLI package
│   │   ├── __init__.py
│   │   └── main.py      # Typer CLI application
│   ├── api.py           # FastAPI server
│   └── core/            # Core functionality
├── docs/                # Optimized documentation storage
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## License

MIT License 