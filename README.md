# LLMContext

A universal sidecar service + CLI tool that detects frameworks/libraries in a developer's codebase, collects and compresses their documentation using an LLM, tags and embeds the results, and serves optimized, RAG-ready context to agents or users via local API, file cache, or CLI.

## 🚀 Features

### Core Capabilities
- **🔍 Framework Detection**: Automatically detects frameworks and libraries across multiple ecosystems
- **📚 Documentation Collection**: Downloads and processes documentation from official sources
- **🧠 LLM Processing**: Compresses documentation using OpenAI's GPT models
- **🏷️ Smart Tagging**: Classifies frameworks with semantic tags (web, api, frontend, etc.)
- **🔢 Vector Embeddings**: Generates embeddings for semantic search
- **💾 Context Caching**: Saves optimized context chunks to disk for offline access
- **🌐 Multiple Interfaces**: CLI, API, and file-based access to context

### Framework Detection
- **Multi-Ecosystem Support**: JavaScript, Python, Ruby, PHP, .NET, Elixir, Haskell, Docker
- **Explicit Dependencies**: Parses package.json, requirements.txt, pyproject.toml, Gemfile, composer.json, *.csproj, mix.exs, stack.yaml, *.cabal, Dockerfile
- **Framework Inference**: Detects frameworks from config files (next.config.js, manage.py, angular.json, etc.)
- **Confidence Scoring**: Assigns confidence levels based on detection method
- **Ecosystem Grouping**: Organizes detected frameworks by language/stack

### Documentation Pipeline
- **Raw Collection**: Downloads documentation from official sites and GitHub
- **Intelligent Chunking**: Splits documents into optimal chunks (800-1200 tokens)
- **LLM Summarization**: Compresses chunks while preserving essential information
- **Progress Tracking**: Visual progress bars for long-running operations
- **Batch Processing**: Efficient handling of multiple documents

### Vector Database
- **ChromaDB Integration**: Local persistent storage for embeddings
- **Semantic Search**: Find relevant context using natural language queries
- **Metadata Storage**: Rich metadata for each context chunk
- **Flexible Queries**: Search by tool, topic, or universal semantic search

### Sidecar Server
- **FastAPI Backend**: High-performance API server
- **Tool Management**: Add, remove, and list configured tools
- **Context Retrieval**: Get optimized context chunks via API
- **Health Monitoring**: Server health and status endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd llmcontext

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Prerequisites
- Python 3.8+
- OpenAI API key (for documentation processing and embeddings)
- Internet connection (for documentation collection)

## 🛠️ Usage

### CLI Commands

#### Project Management
```bash
# Initialize a new project
llmcontext init

# Add frameworks to track
llmcontext add react
llmcontext add tailwind --version 3.3.0
llmcontext add fastapi@0.104.0

# List configured tools
llmcontext list-tools

# Remove a tool
llmcontext remove react

# Get information about tools
llmcontext get
llmcontext get react
```

#### Framework Detection
```bash
# Detect frameworks in current codebase
llmcontext detect

# Detect with custom config file
llmcontext detect --config path/to/config.json
```

#### Documentation Pipeline
```bash
# Collect raw documentation
llmcontext collect react
llmcontext collect --all-tools
llmcontext collect --list-tools

# Chunk documentation files
llmcontext chunk input.md --output-dir chunks/
llmcontext chunk --input-dir raw_docs/ --strategy hybrid

# Summarize documentation chunks
llmcontext summarize chunks/ --output-dir summaries/
llmcontext summarize --api-key YOUR_KEY --model gpt-4o-mini

# Process complete documentation pipeline
llmcontext process react chunks/ --output-dir docs/
```

#### Embeddings & Vector Database
```bash
# Generate embeddings from processed docs
llmcontext embed docs/ --output-dir embeddings/
llmcontext embed --model text-embedding-3-large --batch-size 100

# Manage vector database
llmcontext vectordb add embeddings/
llmcontext vectordb search "how to use useEffect"
llmcontext vectordb info
llmcontext vectordb reset
```

#### Context Querying
```bash
# Universal semantic search
llmcontext query "how to manage state in React"
llmcontext query "async programming patterns" --tool fastapi

# Tool-specific queries
llmcontext query_tool react hooks
llmcontext query_tool tailwind responsive --n-results 10

# Read cached context from disk
llmcontext read-context --list
llmcontext read-context react hooks
```

#### Server Management
```bash
# Start the sidecar server
llmcontext server
llmcontext server --host 0.0.0.0 --port 8001

# Server with auto-reload
llmcontext server --reload
```

### API Server

#### Start the Server
```bash
# Using CLI command
llmcontext server

# Using uvicorn directly
python -m uvicorn sidecar.app:app --reload --host 127.0.0.1 --port 8001
```

#### API Endpoints

**Health & Status**
```bash
GET /health                    # Server health check
GET /                          # API information
```

**Tool Management**
```bash
GET /stack                     # Get configured tools
POST /add-tool                 # Add a new tool
```

**Context Retrieval**
```bash
GET /context                   # Get context by tool and topic
GET /context/vector            # Universal semantic search
GET /tools                     # List available tools in vector DB
GET /topics                    # List available topics
```

#### Example API Usage
```bash
# Add a tool
curl -X POST "http://127.0.0.1:8001/add-tool" \
  -H "Content-Type: application/json" \
  -d '{"tool": "react", "version": "18"}'

# Get configured tools
curl "http://127.0.0.1:8001/stack"

# Search for context
curl "http://127.0.0.1:8001/context/vector?query=useEffect%20hook&n_results=5"

# Get tool-specific context
curl "http://127.0.0.1:8001/context?tool=react&topic=hooks&n_results=10"
```

## ⚙️ Configuration

LLMContext uses a `.llmcontext.json` configuration file to manage project settings and framework tracking.

### Quick Start
```bash
# Initialize configuration
llmcontext init

# Add your first tools
llmcontext add react
llmcontext add tailwind --version 3.3.0
```

### Configuration Schema

**Current Implementation (Simplified)**
```json
{
  "stack": [
    "react@18",
    "tailwind@3.3",
    "fastapi@0.104.0",
    "django@4.2"
  ]
}
```

**Extended Schema (Future)**
```json
{
  "version": "1.0.0",
  "project": {
    "name": "my-project",
    "description": "A modern web application",
    "documentation_dir": "docs",
    "cache_dir": ".llmcontext_cache"
  },
  "settings": {
    "auto_detect": true,
    "include_dev_dependencies": false,
    "embedding_model": "text-embedding-3-large",
    "similarity_threshold": 0.5
  },
  "stack": ["react@18", "tailwind@3.3"],
  "tools": {
    "enabled": ["react", "tailwind"],
    "ignored": ["lodash", "moment"],
    "tool_configs": {
      "react": {
        "version": "18.2.0",
        "detection_patterns": ["package.json", "src/**/*.jsx"],
        "documentation_sources": ["https://react.dev"]
      }
    }
  }
}
```

For complete configuration documentation, see [CONFIGURATION_SCHEMA.md](CONFIGURATION_SCHEMA.md).

## 🔧 Supported Frameworks

### Web Frameworks
- **React** - React.js ecosystem
- **Vue** - Vue.js framework
- **Angular** - Angular framework
- **Svelte** - Svelte framework
- **Next.js** - React framework
- **Nuxt** - Vue framework
- **Remix** - Full-stack React framework
- **Astro** - Static site generator

### CSS Frameworks
- **Tailwind CSS** - Utility-first CSS framework
- **Bootstrap** - CSS framework
- **Bulma** - Modern CSS framework
- **Foundation** - Responsive front-end framework

### Backend Frameworks
- **FastAPI** - Modern Python web framework
- **Django** - Python web framework
- **Flask** - Python micro-framework
- **Express** - Node.js web framework
- **Laravel** - PHP web framework
- **Ruby on Rails** - Ruby web framework
- **Spring Boot** - Java framework
- **Gin** - Go web framework
- **Actix** - Rust web framework

### Infrastructure & Cloud
- **Docker** - Containerization platform
- **Kubernetes** - Container orchestration
- **Terraform** - Infrastructure as code
- **AWS** - Amazon Web Services
- **Azure** - Microsoft Azure
- **Google Cloud Platform** - GCP services

### Additional Ecosystems
- **Ruby** - Ruby programming language
- **PHP** - PHP programming language
- **.NET** - Microsoft .NET framework
- **Elixir** - Elixir programming language
- **Haskell** - Haskell programming language

## 📁 Project Structure

```
llmcontext/
├── llmcontext/
│   ├── __init__.py
│   ├── cli/                    # CLI package
│   │   ├── __init__.py
│   │   └── main.py            # Typer CLI application
│   ├── api.py                 # Main FastAPI server
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── detector.py        # Framework detection
│   │   ├── collector.py       # Documentation collection
│   │   ├── chunker.py         # Document chunking
│   │   ├── summarizer.py      # LLM summarization
│   │   ├── processor.py       # Documentation processing
│   │   ├── embeddings.py      # Embedding generation
│   │   └── vectordb.py        # Vector database operations
│   └── sidecar/               # Sidecar server
│       └── app.py             # FastAPI sidecar server
├── docs/                      # Optimized documentation storage
├── raw_docs/                  # Raw documentation files
├── embeddings/                # Generated embeddings
├── chroma_db/                 # Vector database storage
├── .llmcontext/               # Context cache directory
│   └── context/               # Cached context chunks
├── tests/                     # Test suite
├── pyproject.toml             # Project configuration
├── CONFIGURATION_SCHEMA.md    # Configuration documentation
└── README.md                  # This file
```

## 🔄 Workflow

### 1. Project Setup
```bash
# Initialize project
llmcontext init

# Add frameworks to track
llmcontext add react tailwind fastapi

# Detect existing frameworks
llmcontext detect
```

### 2. Documentation Collection
```bash
# Collect raw documentation
llmcontext collect --all-tools

# Process documentation pipeline
llmcontext process react chunks/ --output-dir docs/
```

### 3. Embeddings & Search
```bash
# Generate embeddings
llmcontext embed docs/ --output-dir embeddings/

# Add to vector database
llmcontext vectordb add embeddings/
```

### 4. Context Retrieval
```bash
# Start sidecar server
llmcontext server

# Query for context
llmcontext query "how to use React hooks"
llmcontext query_tool react state-management
```

## 🚀 Advanced Features

### Framework Detection
- **Multi-file Analysis**: Analyzes package.json, requirements.txt, pyproject.toml, etc.
- **Pattern Matching**: Detects frameworks from file patterns and configurations
- **Confidence Scoring**: Assigns confidence levels (0.9 main, 0.7-0.8 dev, 0.6 inferred)
- **Ecosystem Grouping**: Organizes by language (Python, JavaScript, Ruby, etc.)
- **Tag Classification**: Semantic tags (web, api, frontend, backend, testing, etc.)

### Documentation Processing
- **Intelligent Chunking**: Semantic, token-count, and hybrid strategies
- **LLM Summarization**: GPT-4 powered compression with custom prompts
- **Progress Tracking**: Visual progress bars for long operations
- **Batch Processing**: Efficient handling of multiple files
- **Error Recovery**: Retry logic for API failures

### Vector Search
- **Semantic Search**: Natural language queries across all tools
- **Tool Filtering**: Search within specific frameworks
- **Topic Filtering**: Search within specific topics
- **Similarity Thresholds**: Configurable relevance scoring
- **Metadata Filtering**: Filter by source, version, confidence

### Context Caching
- **Disk Storage**: Persistent context chunks in `.llmcontext/context/`
- **Organized Structure**: `context/<tool>/<topic>.md` format
- **Query Metadata**: Stores search parameters and results
- **Offline Access**: Read cached context without server
- **Automatic Cleanup**: Configurable cache management

## 🔧 Development

### Setup Development Environment
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

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

### Environment Variables
```bash
# Required for LLM features
export OPENAI_API_KEY="your-openai-api-key"

# Optional configuration
export LLMCONTEXT_HOST="127.0.0.1"
export LLMCONTEXT_PORT="8001"
export LLMCONTEXT_CACHE_DIR=".llmcontext/context"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_detector.py
pytest tests/test_collector.py

# Run with coverage
pytest --cov=llmcontext
```

## 📊 Performance

### Optimization Features
- **Batch Processing**: Efficient handling of multiple documents
- **Concurrent Requests**: Configurable parallel processing
- **Caching**: Persistent storage of processed results
- **Progress Tracking**: Visual feedback for long operations
- **Error Recovery**: Automatic retry for transient failures

### Resource Usage
- **Memory**: Efficient chunking reduces memory footprint
- **Storage**: Compressed documentation and embeddings
- **Network**: Batch API calls minimize network overhead
- **CPU**: Configurable concurrency for optimal performance

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints for function signatures
- Add docstrings for all public functions
- Write comprehensive tests
- Update documentation for new features

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** - For GPT models and embedding APIs
- **ChromaDB** - For vector database functionality
- **FastAPI** - For high-performance API framework
- **Typer** - For elegant CLI interface
- **tqdm** - For progress tracking

## 📞 Support

- **Documentation**: [CONFIGURATION_SCHEMA.md](CONFIGURATION_SCHEMA.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Project Wiki

---

**LLMContext** - Your intelligent framework companion for context-aware development! 🚀 