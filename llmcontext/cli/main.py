"""
Main CLI application using Typer.
"""

import json
import os
import typer
import requests
from pathlib import Path
from typing import Optional, List, Dict, Union, Any
from enum import Enum

# Sidecar server configuration
SIDECAR_URL = "http://127.0.0.1:8001"
SIDECAR_TIMEOUT = 5  # seconds


def check_sidecar_available() -> bool:
    """Check if the sidecar server is available."""
    try:
        response = requests.get(f"{SIDECAR_URL}/health", timeout=SIDECAR_TIMEOUT)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def call_sidecar_add_tool(tool: str, version: Optional[str] = None) -> Dict[str, Any]:
    """Call the sidecar server to add a tool."""
    try:
        data = {"tool": tool}
        if version:
            data["version"] = version
        
        response = requests.post(f"{SIDECAR_URL}/add-tool", json=data, timeout=SIDECAR_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise typer.BadParameter(f"Failed to call sidecar server: {str(e)}")


def call_sidecar_get_stack() -> Dict[str, Any]:
    """Call the sidecar server to get the current stack."""
    try:
        response = requests.get(f"{SIDECAR_URL}/stack", timeout=SIDECAR_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise typer.BadParameter(f"Failed to call sidecar server: {str(e)}")


def call_sidecar_get_context(tool: str, topic: str, n_results: int = 10, similarity_threshold: float = 0.5) -> Dict[str, Any]:
    """Call the sidecar server to get context."""
    try:
        params = {
            "tool": tool,
            "topic": topic,
            "n_results": n_results,
            "similarity_threshold": similarity_threshold
        }
        response = requests.get(f"{SIDECAR_URL}/context", params=params, timeout=SIDECAR_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise typer.BadParameter(f"Failed to call sidecar server: {str(e)}")


def call_sidecar_get_tools() -> Dict[str, Any]:
    """Call the sidecar server to get available tools."""
    try:
        response = requests.get(f"{SIDECAR_URL}/tools", timeout=SIDECAR_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise typer.BadParameter(f"Failed to call sidecar server: {str(e)}")


def call_sidecar_get_topics(tool: Optional[str] = None) -> Dict[str, Any]:
    """Call the sidecar server to get available topics."""
    try:
        params = {}
        if tool:
            params["tool"] = tool
        
        response = requests.get(f"{SIDECAR_URL}/topics", params=params, timeout=SIDECAR_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise typer.BadParameter(f"Failed to call sidecar server: {str(e)}")


def handle_sidecar_fallback(operation: str, fallback_func, *args, **kwargs):
    """Handle sidecar fallback when server is not available."""
    if check_sidecar_available():
        try:
            return fallback_func(*args, **kwargs)
        except Exception as e:
            typer.echo(f"WARNING:  Sidecar server error: {e}")
            typer.echo("Falling back to local configuration...")
            return None
    else:
        typer.echo(f"WARNING:  Sidecar server not available at {SIDECAR_URL}")
        typer.echo("Falling back to local configuration...")
        return None


app = typer.Typer(
    name="llmcontext",
    help="Universal sidecar service + CLI for framework detection and documentation optimization",
    add_completion=False,
)


class Tool(str, Enum):
    """Supported tools/frameworks."""
    # Web Frameworks
    REACT = "react"
    TAILWIND = "tailwind"
    PRISMA = "prisma"
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    EXPRESS = "express"
    NEXTJS = "nextjs"
    VUE = "vue"
    ANGULAR = "angular"
    LARAVEL = "laravel"
    RUBY_ON_RAILS = "rails"
    SPRING = "spring"
    GO_GIN = "gin"
    RUST_ACTIX = "actix"
    
    # Infrastructure & Cloud
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    TERRAFORM = "terraform"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    
    # Additional Ecosystems (auto-detected)
    RUBY = "ruby"
    PHP = "php"
    DOTNET = "dotnet"
    ELIXIR = "elixir"
    HASKELL = "haskell"


def get_config_path() -> Path:
    """Get the path to the .llmcontext.json config file."""
    return Path.cwd() / ".llmcontext.json"


def load_config() -> dict:
    """Load the configuration from .llmcontext.json."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            typer.echo("Error: Invalid JSON in .llmcontext.json", err=True)
            return {"stack": []}
    return {"stack": []}


def save_config(config: dict) -> None:
    """Save the configuration to .llmcontext.json."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config file")
):
    """
    Initialize a new LLMContext configuration file.
    
    Creates a .llmcontext.json file in the current directory with default settings.
    """
    config_path = get_config_path()
    
    if config_path.exists() and not force:
        typer.echo(f"Configuration file already exists at {config_path}")
        typer.echo("Use --force to overwrite it.")
        raise typer.Exit(1)
    
    default_config = {
        "stack": []
    }
    
    save_config(default_config)
    typer.echo(f"SUCCESS: Created configuration file: {config_path}")
    typer.echo("📝 Edit the file to customize your settings.")
    typer.echo("TOOLS: Use 'llmcontext add <tool>' to register frameworks.")


@app.command()
def add(
    tool: Tool = typer.Argument(..., help="Tool/framework to add"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific version to track"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    use_sidecar: bool = typer.Option(True, "--sidecar/--no-sidecar", help="Use sidecar server if available")
):
    """
    Add a tool/framework to the LLMContext configuration.
    
    Registers a framework for detection and documentation processing.
    """
    if use_sidecar and check_sidecar_available():
        try:
            # Try to use sidecar server
            result = call_sidecar_add_tool(tool.value, version)
            typer.echo(f"SUCCESS: {result.get('message', 'Tool added successfully')}")
            return
        except Exception as e:
            typer.echo(f"WARNING:  Sidecar server error: {e}")
            typer.echo("Falling back to local configuration...")
    
    # Fallback to local configuration
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"ERROR: Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("ERROR: Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    # Ensure the stack section exists
    if "stack" not in config:
        config["stack"] = []
    
    # Create tool entry with version if specified
    tool_entry = tool.value
    if version:
        tool_entry = f"{tool.value}@{version}"
    
    # Check if tool is already in stack
    for existing_tool in config["stack"]:
        if existing_tool.startswith(f"{tool.value}@"):
            if existing_tool == tool_entry:
                typer.echo(f"WARNING:  Tool '{tool_entry}' is already in the stack.")
                return
            else:
                # Update existing tool with new version
                config["stack"].remove(existing_tool)
                break
        elif existing_tool == tool.value and not version:
            typer.echo(f"WARNING:  Tool '{tool.value}' is already in the stack.")
            return
    
    # Add tool to stack
    config["stack"].append(tool_entry)
    
    # Save updated configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"SUCCESS: Added '{tool_entry}' to stack.")
    
    # Show next steps
    typer.echo(f"SEARCH: Run 'llmcontext detect' to scan for {tool.value} in your codebase.")


@app.command()
def remove(
    tool: str = typer.Argument(..., help="Tool/framework to remove"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """
    Remove a tool/framework from the LLMContext configuration.
    """
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"ERROR: Configuration file not found: {config_path}")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("ERROR: Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    if "stack" not in config:
        typer.echo("ERROR: No tools configured.")
        raise typer.Exit(1)
    
    # Find and remove the tool (with or without version)
    removed = False
    for existing_tool in config["stack"][:]:  # Create a copy to iterate
        if existing_tool == tool or existing_tool.startswith(f"{tool}@"):
            config["stack"].remove(existing_tool)
            removed = True
            break
    
    if not removed:
        typer.echo(f"WARNING:  Tool '{tool}' is not in the stack.")
        return
    
    # Save updated configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"SUCCESS: Removed '{tool}' from stack.")


@app.command()
def get(
    tool: Optional[str] = typer.Argument(None, help="Tool name to get information for"),
    use_sidecar: bool = typer.Option(True, "--sidecar/--no-sidecar", help="Use sidecar server if available")
):
    """
    Get information about configured tools or available tools in the vector database.
    
    If no tool is specified, shows all available tools in the vector database.
    If a tool is specified, shows topics available for that tool.
    """
    if use_sidecar and check_sidecar_available():
        try:
            if tool:
                # Get topics for specific tool
                result = call_sidecar_get_topics(tool)
                topics = result.get("topics", [])
                total = result.get("total_topics", 0)
                
                typer.echo(f"TOPICS: Topics available for '{tool}' ({total} total):")
                if topics:
                    for topic in topics:
                        typer.echo(f"    • {topic}")
                else:
                    typer.echo("  No topics found for this tool.")
            else:
                # Get all available tools
                result = call_sidecar_get_tools()
                tools = result.get("tools", {})
                total = result.get("total_tools", 0)
                
                typer.echo(f"TOOLS:  Available tools in vector database ({total} total):")
                for tool_name, tool_info in tools.items():
                    topics = tool_info.get("topics", [])
                    topic_count = tool_info.get("topic_count", 0)
                    typer.echo(f"    • {tool_name} ({topic_count} topics)")
                    for topic in topics[:5]:  # Show first 5 topics
                        typer.echo(f"    - {topic}")
                    if len(topics) > 5:
                        typer.echo(f"    ... and {len(topics) - 5} more")
            return
        except Exception as e:
            typer.echo(f"WARNING:  Sidecar server error: {e}")
            typer.echo("Falling back to local configuration...")
    
    # Fallback to local configuration
    config_path = get_config_path()
    
    if not config_path.exists():
        typer.echo(f"ERROR: Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("ERROR: Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    if "stack" not in config or not config["stack"]:
        typer.echo("INFO: No tools configured.")
        return
    
    if tool:
        # Check if tool is in stack
        tool_found = False
        for tool_entry in config["stack"]:
            if tool_entry == tool or tool_entry.startswith(f"{tool}@"):
                tool_found = True
                break
        
        if tool_found:
            typer.echo(f"SUCCESS: Tool '{tool}' is configured in the stack.")
        else:
            typer.echo(f"ERROR: Tool '{tool}' is not configured in the stack.")
            typer.echo("Available tools:")
            for tool_entry in config["stack"]:
                if "@" in tool_entry:
                    tool_name, version = tool_entry.split("@", 1)
                    typer.echo(f"    • {tool_name} (version: {version})")
                else:
                    typer.echo(f"    • {tool_entry} (version: latest)")
    else:
        typer.echo("INFO: Configured tools:")
        for tool_entry in config["stack"]:
            if "@" in tool_entry:
                tool_name, version = tool_entry.split("@", 1)
                typer.echo(f"    • {tool_name} (version: {version})")
            else:
                typer.echo(f"    • {tool_entry} (version: latest)")


@app.command()
def query(
    tool: str = typer.Argument(..., help="Tool name to query"),
    topic: str = typer.Argument(..., help="Topic to query"),
    n_results: int = typer.Option(5, "--n-results", "-n", help="Number of results to return"),
    similarity_threshold: float = typer.Option(0.5, "--threshold", "-t", help="Minimum similarity score"),
    use_sidecar: bool = typer.Option(True, "--sidecar/--no-sidecar", help="Use sidecar server if available")
):
    """
    Query the vector database for context about a specific tool and topic.
    
    Returns optimized context chunks from the documentation.
    """
    if use_sidecar and check_sidecar_available():
        try:
            # Try to use sidecar server
            result = call_sidecar_get_context(tool, topic, n_results, similarity_threshold)
            chunks = result.get("chunks", [])
            total_results = result.get("total_results", 0)
            query_info = result.get("query_info", {})
            
            typer.echo(f"SEARCH: Query Results for '{tool}' - '{topic}'")
            typer.echo(f"STATS: Found {total_results} context chunks")
            typer.echo(f"STATS: Search method: {query_info.get('search_method', 'unknown')}")
            typer.echo()
            
            if chunks:
                for i, chunk in enumerate(chunks, 1):
                    typer.echo(f"{i}. {chunk.get('chunk_id', 'Unknown')}")
                    typer.echo(f"   Similarity: {chunk.get('similarity_score', 0):.3f}")
                    typer.echo(f"   Source: {chunk.get('source_file', 'Unknown')}")
                    typer.echo(f"   Content: {chunk.get('content', '')[:200]}...")
                    typer.echo()
            else:
                typer.echo("ERROR: No matching context found.")
                typer.echo("Try:")
                typer.echo("    • Different tool name or topic")
                typer.echo("    • Lower similarity threshold")
                typer.echo("    • Check available tools with 'llmcontext get'")
            return
        except Exception as e:
            typer.echo(f"WARNING:  Sidecar server error: {e}")
            typer.echo("Falling back to local configuration...")
    
    # Fallback to local configuration
    typer.echo("ERROR: Vector database query requires sidecar server.")
    typer.echo("Please start the sidecar server with: python sidecar/app.py")
    typer.echo("Or use the vectordb command for direct database access.")
    raise typer.Exit(1)


@app.command()
def server(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8001, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload on file changes")
):
    """
    Start the LLMContext sidecar server.
    
    The sidecar server provides API endpoints for tool management and context retrieval.
    """
    try:
        import uvicorn
        import sys
        from pathlib import Path
        
        # Get the path to the sidecar app
        sidecar_app_path = Path(__file__).parent.parent.parent / "sidecar" / "app.py"
        
        if not sidecar_app_path.exists():
            typer.echo(f"ERROR: Sidecar app not found at: {sidecar_app_path}")
            typer.echo("Please ensure the sidecar directory exists with app.py")
            raise typer.Exit(1)
        
        typer.echo(f"STARTING: Starting LLMContext sidecar server...")
        typer.echo(f"HOST: Host: {host}")
        typer.echo(f"HOST: Port: {port}")
        typer.echo(f"RELOAD: Auto-reload: {'enabled' if reload else 'disabled'}")
        typer.echo(f"URL: URL: http://{host}:{port}")
        typer.echo(f"TOPICS: API docs: http://{host}:{port}/docs")
        typer.echo()
        typer.echo("Press Ctrl+C to stop the server")
        typer.echo()
        
        # Start the server
        uvicorn.run(
            "sidecar.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        typer.echo("ERROR: uvicorn not installed. Install with: pip install uvicorn")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Failed to start server: {e}")
        raise typer.Exit(1)


@app.command()
def list_tools(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    use_sidecar: bool = typer.Option(True, "--sidecar/--no-sidecar", help="Use sidecar server if available")
):
    """
    List all configured tools/frameworks.
    """
    if use_sidecar and check_sidecar_available():
        try:
            # Try to use sidecar server
            result = call_sidecar_get_stack()
            tools = result.get("tools", [])
            total = result.get("total", 0)
            
            if total == 0:
                typer.echo("INFO: No tools configured.")
                return
            
            typer.echo(f"INFO: Configured tools ({total} total):")
            for tool in tools:
                name = tool.get("name", "Unknown")
                version = tool.get("version", "latest")
                typer.echo(f"    • {name} (version: {version})")
            return
        except Exception as e:
            typer.echo(f"WARNING:  Sidecar server error: {e}")
            typer.echo("Falling back to local configuration...")
    
    # Fallback to local configuration
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"ERROR: Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("ERROR: Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    if "stack" not in config or not config["stack"]:
        typer.echo("INFO: No tools configured.")
        return
    
    typer.echo("INFO: Configured tools:")
    for tool_entry in config["stack"]:
        if "@" in tool_entry:
            tool_name, version = tool_entry.split("@", 1)
            typer.echo(f"    • {tool_name} (version: {version})")
        else:
            typer.echo(f"    • {tool_entry} (version: latest)")


@app.command()
def detect(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """
    Detect frameworks in the current codebase.
    """
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"ERROR: Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    typer.echo("Scanning codebase for frameworks and libraries...")
    
    try:
        from llmcontext.core.detector import FrameworkDetector
        
        detector = FrameworkDetector()
        detected_frameworks = detector.detect_frameworks(Path.cwd())
        
        if not detected_frameworks:
            typer.echo("No frameworks or libraries detected in the current codebase.")
            return
        
        # Group frameworks by ecosystem and dependency type
        ecosystem_groups = _group_frameworks_by_ecosystem(detected_frameworks)
        
        # Display grouped results
        total_files = len(set(f.metadata.get("source", "unknown") for f in detected_frameworks))
        
        for ecosystem, groups in ecosystem_groups.items():
            if not groups:  # Skip empty ecosystems
                continue
                
            typer.echo(f"PACKAGES: {ecosystem} Frameworks")
            
            # Show main dependencies first
            if "main" in groups and groups["main"]:
                for framework in groups["main"]:
                    _display_framework(framework)
            
            # Show dev dependencies
            if "dev" in groups and groups["dev"]:
                typer.echo("  DEV TOOLS: Dev Tools")
                for framework in groups["dev"]:
                    _display_framework(framework, indent="    ")
            
            # Show inferred frameworks
            if "inferred" in groups and groups["inferred"]:
                typer.echo("  SEARCH: Inferred")
                for framework in groups["inferred"]:
                    _display_framework(framework, indent="    ")
            
            # Show ecosystem summary
            ecosystem_count = sum(len(frameworks) for frameworks in groups.values())
            typer.echo(f"    └- {ecosystem_count} frameworks detected")
            typer.echo()
        
        # Show overall summary
        unique_frameworks = len(set(f.name for f in detected_frameworks))
        typer.echo(f"SUCCESS: Total: {unique_frameworks} frameworks detected from {total_files} files")
        
    except ImportError as e:
        typer.echo(f"ERROR: Error importing detector: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during detection: {e}")
        raise typer.Exit(1)


@app.command()
def collect(
    tool: Optional[str] = typer.Argument(None, help="Tool name to collect documentation for"),
    all_tools: bool = typer.Option(False, "--all", "-a", help="Collect documentation for all available tools"),
    force_refresh: bool = typer.Option(False, "--force", "-f", help="Force refresh existing documentation"),
    list_tools: bool = typer.Option(False, "--list", "-l", help="List all available tools for documentation collection")
):
    """Collect documentation for tools and frameworks."""
    import asyncio
    
    try:
        from llmcontext.core.collector import DocumentationCollector
        
        collector = DocumentationCollector()
        
        if list_tools:
            available_tools = collector.get_available_tools()
            typer.echo(f"Available tools for documentation collection ({len(available_tools)}):")
            for tool_name in sorted(available_tools):
                typer.echo(f"    • {tool_name}")
            return
        
        if all_tools:
            typer.echo("Collecting documentation for all available tools...")
            results = asyncio.run(collector.collect_all_documentation(force_refresh))
            
            successful = [name for name, success in results.items() if success]
            failed = [name for name, success in results.items() if not success]
            
            typer.echo(f"\nSUCCESS: Successfully collected documentation for {len(successful)} tools:")
            for tool_name in successful:
                typer.echo(f"    • {tool_name}")
            
            if failed:
                typer.echo(f"\nERROR: Failed to collect documentation for {len(failed)} tools:")
                for tool_name in failed:
                    typer.echo(f"    • {tool_name}")
            
            return
        
        if not tool:
            typer.echo("ERROR: Please specify a tool name or use --all to collect for all tools")
            typer.echo("Use --list to see available tools")
            raise typer.Exit(1)
        
        typer.echo(f"Collecting documentation for {tool}...")
        success = asyncio.run(collector.collect_documentation(tool, force_refresh))
        
        if success:
            typer.echo(f"SUCCESS: Successfully collected documentation for {tool}")
            typer.echo(f"DIR: Documentation saved to: raw_docs/{tool}.md")
        else:
            typer.echo(f"ERROR: Failed to collect documentation for {tool}")
            typer.echo("Use --list to see available tools")
            raise typer.Exit(1)
            
    except ImportError as e:
        typer.echo(f"ERROR: Error importing collector: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during collection: {e}")
        raise typer.Exit(1)


@app.command()
def chunk(
    input_file: Optional[Path] = typer.Argument(None, help="Input documentation file to chunk"),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", "-i", help="Input directory containing documentation files"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for chunks"),
    target_size: int = typer.Option(1000, "--target-size", "-t", help="Target chunk size in tokens"),
    min_size: int = typer.Option(800, "--min-size", help="Minimum chunk size in tokens"),
    max_size: int = typer.Option(1200, "--max-size", help="Maximum chunk size in tokens"),
    overlap: int = typer.Option(100, "--overlap", help="Overlap between chunks in tokens"),
    strategy: str = typer.Option("hybrid", "--strategy", "-s", help="Chunking strategy: semantic, token_count, or hybrid")
):
    """Chunk documentation files into optimal sizes for LLM processing."""
    try:
        from llmcontext.core.chunker import DocumentationChunker, ChunkStrategy
        
        # Parse strategy
        strategy_map = {
            "semantic": ChunkStrategy.SEMANTIC,
            "token_count": ChunkStrategy.TOKEN_COUNT,
            "hybrid": ChunkStrategy.HYBRID
        }
        
        if strategy not in strategy_map:
            typer.echo(f"ERROR: Invalid strategy: {strategy}")
            typer.echo("Valid strategies: semantic, token_count, hybrid")
            raise typer.Exit(1)
        
        chunker = DocumentationChunker(
            target_chunk_size=target_size,
            min_chunk_size=min_size,
            max_chunk_size=max_size,
            overlap_tokens=overlap,
            strategy=strategy_map[strategy]
        )
        
        if input_file:
            # Chunk single file
            if not input_file.exists():
                typer.echo(f"ERROR: Input file not found: {input_file}")
                raise typer.Exit(1)
            
            typer.echo(f"Chunking file: {input_file}")
            chunks = chunker.chunk_file(input_file, output_dir)
            
            # Show statistics
            stats = chunker.get_chunk_statistics(chunks)
            typer.echo(f"SUCCESS: Created {stats['total_chunks']} chunks")
            typer.echo(f"STATS: Total tokens: {stats['total_tokens']}")
            typer.echo(f"STATS: Average tokens per chunk: {stats['average_tokens']:.1f}")
            typer.echo(f"STATS: Token distribution: {stats['token_distribution']}")
            
            if output_dir:
                typer.echo(f"DIR: Chunks saved to: {output_dir}")
        
        elif input_dir:
            # Chunk directory
            if not input_dir.exists():
                typer.echo(f"ERROR: Input directory not found: {input_dir}")
                raise typer.Exit(1)
            
            if not output_dir:
                output_dir = Path("chunks")
            
            typer.echo(f"Chunking directory: {input_dir}")
            typer.echo(f"Output directory: {output_dir}")
            
            results = {}
            total_chunks = 0
            total_tokens = 0
            
            for file_path in input_dir.glob("*.md"):
                try:
                    chunks = chunker.chunk_file(file_path, output_dir)
                    results[str(file_path)] = chunks
                    total_chunks += len(chunks)
                    total_tokens += sum(chunker.count_tokens(chunk.content) for chunk in chunks)
                    
                    typer.echo(f"  SUCCESS: {file_path.name}: {len(chunks)} chunks")
                    
                except Exception as e:
                    typer.echo(f"  ERROR: Error chunking {file_path.name}: {e}")
                    continue
            
            typer.echo(f"\nSUCCESS: Total: {total_chunks} chunks from {len(results)} files")
            typer.echo(f"STATS: Total tokens: {total_tokens}")
            typer.echo(f"DIR: Chunks saved to: {output_dir}")
        
        else:
            typer.echo("ERROR: Please specify either --input-file or --input-dir")
            raise typer.Exit(1)
            
    except ImportError as e:
        typer.echo(f"ERROR: Error importing chunker: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during chunking: {e}")
        raise typer.Exit(1)


@app.command()
def summarize(
    input_file: Optional[Path] = typer.Argument(None, help="Input documentation file to summarize"),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", "-i", help="Input directory containing documentation files"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for summarized files"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model to use for summarization"),
    framework_name: str = typer.Option("unknown", "--framework", "-f", help="Name of the framework/tool being summarized"),
    max_concurrent: int = typer.Option(5, "--max-concurrent", help="Maximum concurrent API calls"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be processed without making API calls")
):
    """Summarize documentation files using OpenAI's GPT-4 API."""
    try:
        from llmcontext.core.summarizer import DocumentationSummarizer
        
        # Check for API key
        if not api_key and not os.getenv("OPENAI_API_KEY"):
            typer.echo("ERROR: OpenAI API key is required.")
            typer.echo("Set OPENAI_API_KEY environment variable or use --api-key option")
            raise typer.Exit(1)
        
        summarizer = DocumentationSummarizer(
            api_key=api_key,
            model=model,
            max_concurrent=max_concurrent
        )
        
        if dry_run:
            typer.echo("SEARCH: DRY RUN MODE - No API calls will be made")
            
            if input_file:
                typer.echo(f"Would summarize: {input_file}")
            elif input_dir:
                files = list(input_dir.glob("*.md"))
                typer.echo(f"Would summarize {len(files)} files from: {input_dir}")
                for file in files:
                    typer.echo(f"    • {file.name}")
            else:
                typer.echo("ERROR: Please specify either --input-file or --input-dir")
                raise typer.Exit(1)
            return
        
        if input_file:
            # Summarize single file
            if not input_file.exists():
                typer.echo(f"ERROR: Input file not found: {input_file}")
                raise typer.Exit(1)
            
            typer.echo(f"Summarizing file: {input_file}")
            result = summarizer.summarize_file(input_file, output_dir)
            
            # Show results
            typer.echo(f"SUCCESS: Summarized: {input_file.name}")
            typer.echo(f"STATS: Token reduction: {result.token_reduction:.1f}%")
            typer.echo(f"STATS: Original tokens: {result.original_tokens}")
            typer.echo(f"STATS: Summarized tokens: {result.summarized_tokens}")
            typer.echo(f"TIME:  Processing time: {result.processing_time:.2f}s")
            
            if output_dir:
                typer.echo(f"DIR: Summary saved to: {output_dir}")
        
        elif input_dir:
            # Summarize directory
            if not input_dir.exists():
                typer.echo(f"ERROR: Input directory not found: {input_dir}")
                raise typer.Exit(1)
            
            if not output_dir:
                output_dir = Path("summarized")
            
            typer.echo(f"Summarizing directory: {input_dir}")
            typer.echo(f"Output directory: {output_dir}")
            typer.echo(f"Model: {model}")
            typer.echo(f"Framework: {framework_name}")
            
            results = summarizer.summarize_directory(input_dir, output_dir, framework_name)
            
            # Show statistics
            stats = summarizer.get_summary_statistics(results)
            typer.echo(f"\nSUCCESS: Summarized {stats['total_files']} files")
            typer.echo(f"STATS: Overall reduction: {stats['overall_reduction_percent']:.1f}%")
            typer.echo(f"STATS: Average reduction: {stats['average_reduction_percent']:.1f}%")
            typer.echo(f"STATS: Total processing time: {stats['total_processing_time']:.2f}s")
            typer.echo(f"STATS: Token distribution: {stats['token_distribution']}")
            typer.echo(f"DIR: Summaries saved to: {output_dir}")
        
        else:
            typer.echo("ERROR: Please specify either --input-file or --input-dir")
            raise typer.Exit(1)
            
    except ImportError as e:
        typer.echo(f"ERROR: Error importing summarizer: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during summarization: {e}")
        raise typer.Exit(1)


@app.command()
def process(
    tool_name: str = typer.Argument(..., help="Name of the tool to process"),
    chunks_dir: Path = typer.Argument(..., help="Directory containing chunk files"),
    output_dir: Path = typer.Option(Path("docs"), "--output-dir", "-o", help="Output directory for processed files"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model to use for summarization"),
    topics: Optional[str] = typer.Option(None, "--topics", "-t", help="Comma-separated list of topics to process"),
    preserve_original: bool = typer.Option(True, "--preserve-original", help="Preserve original chunks in output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be processed without making API calls")
):
    """Process all documentation chunks for a tool using the summarizer."""
    try:
        from llmcontext.core.processor import DocumentationProcessor
        
        # Check for API key
        if not api_key and not os.getenv("OPENAI_API_KEY"):
            typer.echo("ERROR: OpenAI API key is required.")
            typer.echo("Set OPENAI_API_KEY environment variable or use --api-key option")
            raise typer.Exit(1)
        
        # Parse topics
        topic_list = None
        if topics:
            topic_list = [t.strip() for t in topics.split(",")]
        
        processor = DocumentationProcessor(
            api_key=api_key,
            model=model,
            output_base_dir=output_dir,
            preserve_original=preserve_original
        )
        
        if dry_run:
            typer.echo("SEARCH: DRY RUN MODE - No API calls will be made")
            typer.echo(f"Tool: {tool_name}")
            typer.echo(f"Chunks directory: {chunks_dir}")
            typer.echo(f"Output directory: {output_dir}")
            if topic_list:
                typer.echo(f"Topics: {', '.join(topic_list)}")
            else:
                typer.echo("Topics: All available")
            return
        
        # Check if chunks directory exists
        if not chunks_dir.exists():
            typer.echo(f"ERROR: Chunks directory not found: {chunks_dir}")
            raise typer.Exit(1)
        
        typer.echo(f"Processing documentation for tool: {tool_name}")
        typer.echo(f"Chunks directory: {chunks_dir}")
        typer.echo(f"Output directory: {output_dir}")
        typer.echo(f"Model: {model}")
        if topic_list:
            typer.echo(f"Topics: {', '.join(topic_list)}")
        else:
            typer.echo("Topics: All available")
        
        # Process documentation
        results = processor.process_tool_documentation(tool_name, chunks_dir, topic_list)
        
        # Show results
        typer.echo(f"\nSUCCESS: Processing completed!")
        typer.echo(f"STATS: Topics processed: {len(results)}")
        
        total_original_chunks = sum(len(result.original_chunks) for result in results.values())
        total_summarized_chunks = sum(len(result.summarized_chunks) for result in results.values())
        total_processing_time = sum(result.processing_stats['total_processing_time'] for result in results.values())
        
        typer.echo(f"STATS: Total chunks: {total_original_chunks} → {total_summarized_chunks}")
        typer.echo(f"TIME:  Total processing time: {total_processing_time:.2f}s")
        
        # Show per-topic results
        for topic, result in results.items():
            stats = result.processing_stats
            typer.echo(f"    • {topic}: {len(result.original_chunks)} chunks, {stats['overall_reduction_percent']:.1f}% reduction")
        
        typer.echo(f"\nDIR: Output saved to: {output_dir}/{tool_name}/")
        typer.echo(f"FILES: Files created:")
        for topic in results.keys():
            typer.echo(f"    • {tool_name}/{topic}/{topic}.md")
            typer.echo(f"    • {tool_name}/{topic}/{topic}.json")
        typer.echo(f"    • {tool_name}/{tool_name}_summary.md")
        
    except ImportError as e:
        typer.echo(f"ERROR: Error importing processor: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during processing: {e}")
        raise typer.Exit(1)


@app.command()
def embed(
    docs_dir: Path = typer.Argument(..., help="Directory containing processed documentation"),
    output_dir: Path = typer.Option(Path("embeddings"), "--output-dir", "-o", help="Output directory for embeddings"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"),
    model: str = typer.Option("text-embedding-3-large", "--model", "-m", help="OpenAI embedding model to use"),
    tools: Optional[str] = typer.Option(None, "--tools", "-t", help="Comma-separated list of tools to process"),
    topics: Optional[str] = typer.Option(None, "--topics", help="Comma-separated list of topics to process"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Number of texts to embed in a single API call"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be processed without making API calls")
):
    """Generate embeddings from processed documentation chunks."""
    try:
        from llmcontext.core.embeddings import EmbeddingGenerator
        
        # Check for API key
        if not api_key and not os.getenv("OPENAI_API_KEY"):
            typer.echo("ERROR: OpenAI API key is required.")
            typer.echo("Set OPENAI_API_KEY environment variable or use --api-key option")
            raise typer.Exit(1)
        
        # Parse tools and topics
        tools_list = None
        if tools:
            tools_list = [t.strip() for t in tools.split(",")]
        
        topics_list = None
        if topics:
            topics_list = [t.strip() for t in topics.split(",")]
        
        generator = EmbeddingGenerator(
            api_key=api_key,
            model=model,
            batch_size=batch_size,
            output_dir=output_dir
        )
        
        if dry_run:
            typer.echo("SEARCH: DRY RUN MODE - No API calls will be made")
            typer.echo(f"Documentation directory: {docs_dir}")
            typer.echo(f"Output directory: {output_dir}")
            typer.echo(f"Model: {model}")
            typer.echo(f"Batch size: {batch_size}")
            if tools_list:
                typer.echo(f"Tools: {', '.join(tools_list)}")
            else:
                typer.echo("Tools: All available")
            if topics_list:
                typer.echo(f"Topics: {', '.join(topics_list)}")
            else:
                typer.echo("Topics: All available")
            return
        
        # Check if docs directory exists
        if not docs_dir.exists():
            typer.echo(f"ERROR: Documentation directory not found: {docs_dir}")
            raise typer.Exit(1)
        
        typer.echo(f"Generating embeddings from processed documentation...")
        typer.echo(f"Documentation directory: {docs_dir}")
        typer.echo(f"Output directory: {output_dir}")
        typer.echo(f"Model: {model}")
        typer.echo(f"Batch size: {batch_size}")
        if tools_list:
            typer.echo(f"Tools: {', '.join(tools_list)}")
        if topics_list:
            typer.echo(f"Topics: {', '.join(topics_list)}")
        
        # Generate embeddings
        results = generator.generate_embeddings_from_processed_docs(
            docs_dir, tools_list, topics_list
        )
        
        # Show results
        stats = generator.get_embedding_statistics(results)
        
        typer.echo(f"\nSUCCESS: Embedding generation completed!")
        typer.echo(f"STATS: Tools processed: {stats['total_tools']}")
        typer.echo(f"STATS: Topics processed: {stats['total_topics']}")
        typer.echo(f"STATS: Total embeddings: {stats['total_embeddings']}")
        typer.echo(f"STATS: Total tokens: {stats['total_tokens']}")
        typer.echo(f"TIME:  Total processing time: {stats['total_processing_time']:.2f}s")
        typer.echo(f"STATS: Embeddings per second: {stats['embeddings_per_second']:.2f}")
        typer.echo(f"STATS: Average processing time per embedding: {stats['average_processing_time_per_embedding']:.3f}s")
        
        # Show per-tool results
        for tool_name, tool_results in results.items():
            tool_embeddings = sum(len(batch.embeddings) for batch in tool_results.values())
            tool_topics = len(tool_results)
            typer.echo(f"    • {tool_name}: {tool_embeddings} embeddings from {tool_topics} topics")
        
        typer.echo(f"\nDIR: Embeddings saved to: {output_dir}/")
        typer.echo(f"FILES: File formats:")
        typer.echo(f"    • <tool>/<topic>_embeddings.json - Full data with metadata")
        typer.echo(f"    • <tool>/<topic>_embeddings.npy - Numpy array for efficient loading")
        typer.echo(f"    • <tool>/<topic>_metadata.json - Batch metadata")
        
    except ImportError as e:
        typer.echo(f"ERROR: Error importing embeddings module: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during embedding generation: {e}")
        raise typer.Exit(1)


@app.command()
def vectordb(
    action: str = typer.Argument(..., help="Action to perform: add, search, info, list, reset"),
    embeddings_dir: Optional[Path] = typer.Argument(None, help="Directory containing embeddings files"),
    query: Optional[str] = typer.Argument(None, help="Search query"),
    persist_dir: Path = typer.Option(Path("chroma_db"), "--persist-dir", "-p", help="ChromaDB persist directory"),
    collection_name: str = typer.Option("llmcontext_docs", "--collection", "-c", help="Collection name"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"),
    tools: Optional[str] = typer.Option(None, "--tools", "-t", help="Comma-separated list of tools to process"),
    topics: Optional[str] = typer.Option(None, "--topics", help="Comma-separated list of topics to process"),
    n_results: int = typer.Option(10, "--n-results", "-n", help="Number of search results to return"),
    tool_filter: Optional[str] = typer.Option(None, "--tool-filter", help="Filter search results by tool"),
    topic_filter: Optional[str] = typer.Option(None, "--topic-filter", help="Filter search results by topic"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Batch size for adding embeddings"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes")
):
    """Manage ChromaDB vector database for embeddings."""
    try:
        from llmcontext.core.vectordb import VectorDatabase
        
        # Check for API key if needed
        if action == "add" and not api_key and not os.getenv("OPENAI_API_KEY"):
            typer.echo("ERROR: OpenAI API key is required for adding embeddings.")
            typer.echo("Set OPENAI_API_KEY environment variable or use --api-key option")
            raise typer.Exit(1)
        
        # Parse tools and topics
        tools_list = None
        if tools:
            tools_list = [t.strip() for t in tools.split(",")]
        
        topics_list = None
        if topics:
            topics_list = [t.strip() for t in topics.split(",")]
        
        # Initialize vector database
        db = VectorDatabase(
            persist_directory=persist_dir,
            collection_name=collection_name,
            api_key=api_key
        )
        
        if action == "add":
            if not embeddings_dir:
                typer.echo("ERROR: embeddings_dir is required for 'add' action")
                raise typer.Exit(1)
            
            if dry_run:
                typer.echo("SEARCH: DRY RUN MODE - No changes will be made")
                typer.echo(f"Would add embeddings from: {embeddings_dir}")
                typer.echo(f"Persist directory: {persist_dir}")
                typer.echo(f"Collection: {collection_name}")
                if tools_list:
                    typer.echo(f"Tools: {', '.join(tools_list)}")
                if topics_list:
                    typer.echo(f"Topics: {', '.join(topics_list)}")
                return
            
            if not embeddings_dir.exists():
                typer.echo(f"ERROR: Embeddings directory not found: {embeddings_dir}")
                raise typer.Exit(1)
            
            typer.echo(f"Adding embeddings to vector database...")
            typer.echo(f"Embeddings directory: {embeddings_dir}")
            typer.echo(f"Persist directory: {persist_dir}")
            typer.echo(f"Collection: {collection_name}")
            
            result = db.add_embeddings_from_directory(
                embeddings_dir, tools_list, topics_list, batch_size
            )
            
            typer.echo(f"\nSUCCESS: Embeddings added successfully!")
            typer.echo(f"STATS: Files processed: {result['files_processed']}")
            typer.echo(f"STATS: Total embeddings added: {result['total_added']}")
            
            if result['results']:
                typer.echo(f"\nFILES: File results:")
                for file_result in result['results']:
                    typer.echo(f"    • {file_result['file']}: {file_result['added_embeddings']} embeddings")
        
        elif action == "search":
            if not query:
                typer.echo("ERROR: query is required for 'search' action")
                raise typer.Exit(1)
            
            typer.echo(f"Searching vector database...")
            typer.echo(f"Query: '{query}'")
            typer.echo(f"Results: {n_results}")
            
            # Build filter metadata
            filter_metadata = None
            if tool_filter or topic_filter:
                filter_metadata = {}
                if tool_filter:
                    filter_metadata['tool_name'] = tool_filter
                    typer.echo(f"Tool filter: {tool_filter}")
                if topic_filter:
                    filter_metadata['topic'] = topic_filter
                    typer.echo(f"Topic filter: {topic_filter}")
            
            results = db.search_by_text(query, n_results, filter_metadata)
            
            if not results:
                typer.echo("ERROR: No results found")
                return
            
            typer.echo(f"\nSUCCESS: Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                typer.echo(f"\n{i}. {result.chunk_id}")
                typer.echo(f"   Tool: {result.tool_name}")
                typer.echo(f"   Topic: {result.topic}")
                typer.echo(f"   Similarity: {result.similarity_score:.3f}")
                typer.echo(f"   Source: {result.source_file}")
                typer.echo(f"   Content: {result.content[:100]}...")
        
        elif action == "info":
            info = db.get_collection_info()
            
            typer.echo(f"Vector Database Information:")
            typer.echo(f"STATS: Collection: {info.name}")
            typer.echo(f"STATS: Total documents: {info.count}")
            typer.echo(f"STATS: Metadata: {info.metadata}")
            
            # Get available tools and topics
            tools = db.get_tools()
            typer.echo(f"STATS: Available tools ({len(tools)}): {', '.join(tools)}")
            
            topics = db.get_topics()
            typer.echo(f"STATS: Available topics ({len(topics)}): {', '.join(topics)}")
        
        elif action == "list":
            if tool_filter:
                # List topics for specific tool
                topics = db.get_topics(tool_filter)
                typer.echo(f"Topics for tool '{tool_filter}' ({len(topics)}):")
                for topic in topics:
                    typer.echo(f"    • {topic}")
            else:
                # List tools
                tools = db.get_tools()
                typer.echo(f"Available tools ({len(tools)}):")
                for tool in tools:
                    topics = db.get_topics(tool)
                    typer.echo(f"    • {tool} ({len(topics)} topics)")
                    for topic in topics:
                        typer.echo(f"    - {topic}")
        
        elif action == "reset":
            if dry_run:
                typer.echo("SEARCH: DRY RUN MODE - No changes will be made")
                typer.echo(f"Would reset collection: {collection_name}")
                return
            
            typer.echo(f"Resetting collection: {collection_name}")
            success = db.reset_collection()
            
            if success:
                typer.echo("SUCCESS: Collection reset successfully")
            else:
                typer.echo("ERROR: Failed to reset collection")
                raise typer.Exit(1)
        
        else:
            typer.echo(f"ERROR: Unknown action: {action}")
            typer.echo("Valid actions: add, search, info, list, reset")
            raise typer.Exit(1)
        
    except ImportError as e:
        typer.echo(f"ERROR: Error importing vectordb module: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: Error during vector database operation: {e}")
        raise typer.Exit(1)


def _group_frameworks_by_ecosystem(frameworks: List) -> Dict[str, Dict[str, List]]:
    """
    Group frameworks by ecosystem and dependency type.
    
    Args:
        frameworks: List of DetectedFramework objects
        
    Returns:
        Dictionary grouped by ecosystem and dependency type
    """
    ecosystem_groups = {}
    
    for framework in frameworks:
        # Determine ecosystem based on source and metadata
        ecosystem = _determine_ecosystem(framework)
        
        # Determine dependency type
        dep_type = _determine_dependency_type(framework)
        
        # Initialize ecosystem if not exists
        if ecosystem not in ecosystem_groups:
            ecosystem_groups[ecosystem] = {"main": [], "dev": [], "inferred": []}
        
        # Add to appropriate group
        ecosystem_groups[ecosystem][dep_type].append(framework)
    
    return ecosystem_groups


def _determine_ecosystem(framework) -> str:
    """Determine the ecosystem for a framework."""
    source = framework.metadata.get("source", "")
    
    # Map sources to ecosystems
    ecosystem_map = {
        "requirements.txt": "Python",
        "pyproject.toml": "Python",
        "setup.py": "Python",
        "Pipfile": "Python",
        "package.json": "JavaScript",
        "Gemfile": "Ruby",
        "Gemfile.lock": "Ruby",
        "composer.json": "PHP",
        "composer.lock": "PHP",
        ".csproj": ".NET",
        "global.json": ".NET",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java",
        "build.gradle": "Java",
        "mix.exs": "Elixir",
        "stack.yaml": "Haskell",
        ".cabal": "Haskell",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker",
        "docker-compose.yaml": "Docker",
        "inferred": "Inferred",
    }
    
    # Check for exact source match
    if source in ecosystem_map:
        return ecosystem_map[source]
    
    # Check for partial matches
    for key, ecosystem in ecosystem_map.items():
        if key in source:
            return ecosystem
    
    # Default based on framework name patterns
    name = framework.name.lower()
    if any(pattern in name for pattern in ["react", "vue", "angular", "next", "nuxt", "vite", "svelte"]):
        return "JavaScript"
    elif any(pattern in name for pattern in ["django", "flask", "fastapi", "pytest", "mypy"]):
        return "Python"
    elif any(pattern in name for pattern in ["spring", "hibernate", "junit"]):
        return "Java"
    elif any(pattern in name for pattern in ["rails", "sinatra"]):
        return "Ruby"
    elif any(pattern in name for pattern in ["laravel", "symfony"]):
        return "PHP"
    
    return "Other"


def _determine_dependency_type(framework) -> str:
    """Determine if a framework is main, dev, or inferred dependency."""
    metadata = framework.metadata
    
    # Check if it's inferred
    if metadata.get("inferred", False):
        return "inferred"
    
    # Check for dev dependency indicators
    source = metadata.get("source", "")
    dep_type = metadata.get("type", "")
    confidence = framework.confidence
    
    # Dev dependency indicators
    dev_indicators = [
        "devDependencies",
        "require-dev",
        "optional-dependencies",
        "group :development",
        "group :test",
        "test",
        "dev",
        "development"
    ]
    
    if any(indicator in str(metadata) for indicator in dev_indicators):
        return "dev"
    
    # Lower confidence often indicates dev dependencies
    if confidence < 0.8:
        return "dev"
    
    return "main"


def _display_framework(framework, indent: str = "  ") -> None:
    """Display a single framework with proper formatting."""
    # Format version
    version_info = f" (v{framework.version})" if framework.version else ""
    
    # Format source file
    source = framework.metadata.get("source", "unknown")
    source_info = f" [{source}]"
    
    # Format confidence (only show if not 0.9)
    confidence_info = ""
    if framework.confidence < 0.9:
        confidence_info = f" [confidence: {framework.confidence:.1f}]"
    
    # Format tags
    tags_info = ""
    if hasattr(framework, 'tags') and framework.tags:
        tags_info = f" [tags: {', '.join(framework.tags)}]"
    
    # Build the display string
    display_parts = [
        f"{indent}  • {framework.name}{version_info}{source_info}{confidence_info}{tags_info}"
    ]
    
    typer.echo("".join(display_parts))


def get_default_patterns(tool: Tool) -> List[str]:
    """Get default detection patterns for a tool."""
    patterns = {
        Tool.REACT: ["package.json", "src/**/*.jsx", "src/**/*.tsx"],
        Tool.TAILWIND: ["tailwind.config.js", "tailwind.config.ts", "**/*.css"],
        Tool.PRISMA: ["prisma/schema.prisma", "package.json"],
        Tool.FASTAPI: ["requirements.txt", "pyproject.toml", "**/*.py"],
        Tool.DJANGO: ["manage.py", "settings.py", "urls.py"],
        Tool.FLASK: ["app.py", "requirements.txt", "**/*.py"],
        Tool.EXPRESS: ["package.json", "app.js", "server.js"],
        Tool.NEXTJS: ["next.config.js", "package.json"],
        Tool.VUE: ["package.json", "vue.config.js", "**/*.vue"],
        Tool.ANGULAR: ["angular.json", "package.json"],
        Tool.LARAVEL: ["composer.json", "artisan"],
        Tool.RUBY_ON_RAILS: ["Gemfile", "config/routes.rb"],
        Tool.SPRING: ["pom.xml", "build.gradle"],
        Tool.GO_GIN: ["go.mod", "main.go"],
        Tool.RUST_ACTIX: ["Cargo.toml", "src/main.rs"],
        Tool.DOCKER: ["Dockerfile", "docker-compose.yml"],
        Tool.KUBERNETES: ["*.yaml", "*.yml"],
        Tool.TERRAFORM: ["*.tf", "*.tfvars"],
        Tool.AWS: ["serverless.yml", "template.yaml"],
        Tool.AZURE: ["azure-pipelines.yml", "host.json"],
        Tool.GCP: ["app.yaml", "cloudbuild.yaml"]
    }
    return patterns.get(tool, [])


def get_documentation_sources(tool: Tool) -> List[str]:
    """Get default documentation sources for a tool."""
    sources = {
        Tool.REACT: ["https://react.dev", "https://legacy.reactjs.org"],
        Tool.TAILWIND: ["https://tailwindcss.com/docs"],
        Tool.PRISMA: ["https://www.prisma.io/docs"],
        Tool.FASTAPI: ["https://fastapi.tiangolo.com"],
        Tool.DJANGO: ["https://docs.djangoproject.com"],
        Tool.FLASK: ["https://flask.palletsprojects.com"],
        Tool.EXPRESS: ["https://expressjs.com"],
        Tool.NEXTJS: ["https://nextjs.org/docs"],
        Tool.VUE: ["https://vuejs.org/guide"],
        Tool.ANGULAR: ["https://angular.io/docs"],
        Tool.LARAVEL: ["https://laravel.com/docs"],
        Tool.RUBY_ON_RAILS: ["https://guides.rubyonrails.org"],
        Tool.SPRING: ["https://spring.io/guides"],
        Tool.GO_GIN: ["https://gin-gonic.com/docs"],
        Tool.RUST_ACTIX: ["https://actix.rs/docs"],
        Tool.DOCKER: ["https://docs.docker.com"],
        Tool.KUBERNETES: ["https://kubernetes.io/docs"],
        Tool.TERRAFORM: ["https://developer.hashicorp.com/terraform/docs"],
        Tool.AWS: ["https://docs.aws.amazon.com"],
        Tool.AZURE: ["https://docs.microsoft.com/en-us/azure"],
        Tool.GCP: ["https://cloud.google.com/docs"]
    }
    return sources.get(tool, [])


if __name__ == "__main__":
    app() 