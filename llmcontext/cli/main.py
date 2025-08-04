"""
Main CLI application using Typer.
"""

import json
import typer
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum

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
    typer.echo(f"✅ Created configuration file: {config_path}")
    typer.echo("📝 Edit the file to customize your settings.")
    typer.echo("🔧 Use 'llmcontext add <tool>' to register frameworks.")


@app.command()
def add(
    tool: Tool = typer.Argument(..., help="Tool/framework to add"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific version to track"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """
    Add a tool/framework to the LLMContext configuration.
    
    Registers a framework for detection and documentation processing.
    """
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"❌ Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("❌ Invalid JSON in configuration file.")
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
                typer.echo(f"⚠️  Tool '{tool_entry}' is already in the stack.")
                return
            else:
                # Update existing tool with new version
                config["stack"].remove(existing_tool)
                break
        elif existing_tool == tool.value and not version:
            typer.echo(f"⚠️  Tool '{tool.value}' is already in the stack.")
            return
    
    # Add tool to stack
    config["stack"].append(tool_entry)
    
    # Save updated configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"✅ Added '{tool_entry}' to stack.")
    
    # Show next steps
    typer.echo(f"🔍 Run 'llmcontext detect' to scan for {tool.value} in your codebase.")


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
        typer.echo(f"❌ Configuration file not found: {config_path}")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("❌ Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    if "stack" not in config:
        typer.echo("❌ No tools configured.")
        raise typer.Exit(1)
    
    # Find and remove the tool (with or without version)
    removed = False
    for existing_tool in config["stack"][:]:  # Create a copy to iterate
        if existing_tool == tool or existing_tool.startswith(f"{tool}@"):
            config["stack"].remove(existing_tool)
            removed = True
            break
    
    if not removed:
        typer.echo(f"⚠️  Tool '{tool}' is not in the stack.")
        return
    
    # Save updated configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"✅ Removed '{tool}' from stack.")


@app.command()
def list_tools(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """
    List all configured tools/frameworks.
    """
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"❌ Configuration file not found: {config_path}")
        typer.echo("Run 'llmcontext init' to create a configuration file.")
        raise typer.Exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        typer.echo("❌ Invalid JSON in configuration file.")
        raise typer.Exit(1)
    
    if "stack" not in config or not config["stack"]:
        typer.echo("📋 No tools configured.")
        return
    
    typer.echo("📋 Configured tools:")
    for tool_entry in config["stack"]:
        if "@" in tool_entry:
            tool_name, version = tool_entry.split("@", 1)
            typer.echo(f"  • {tool_name} (version: {version})")
        else:
            typer.echo(f"  • {tool_entry} (version: latest)")


@app.command()
def detect(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """
    Detect frameworks in the current codebase.
    """
    config_path = config_file or get_config_path()
    
    if not config_path.exists():
        typer.echo(f"❌ Configuration file not found: {config_path}")
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
                
            typer.echo(f"📦 {ecosystem} Frameworks")
            
            # Show main dependencies first
            if "main" in groups and groups["main"]:
                for framework in groups["main"]:
                    _display_framework(framework)
            
            # Show dev dependencies
            if "dev" in groups and groups["dev"]:
                typer.echo("  🧪 Dev Tools")
                for framework in groups["dev"]:
                    _display_framework(framework, indent="    ")
            
            # Show inferred frameworks
            if "inferred" in groups and groups["inferred"]:
                typer.echo("  🔍 Inferred")
                for framework in groups["inferred"]:
                    _display_framework(framework, indent="    ")
            
            # Show ecosystem summary
            ecosystem_count = sum(len(frameworks) for frameworks in groups.values())
            typer.echo(f"  └─ {ecosystem_count} frameworks detected")
            typer.echo()
        
        # Show overall summary
        unique_frameworks = len(set(f.name for f in detected_frameworks))
        typer.echo(f"✅ Total: {unique_frameworks} frameworks detected from {total_files} files")
        
    except ImportError as e:
        typer.echo(f"❌ Error importing detector: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error during detection: {e}")
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
                typer.echo(f"  • {tool_name}")
            return
        
        if all_tools:
            typer.echo("Collecting documentation for all available tools...")
            results = asyncio.run(collector.collect_all_documentation(force_refresh))
            
            successful = [name for name, success in results.items() if success]
            failed = [name for name, success in results.items() if not success]
            
            typer.echo(f"\n✅ Successfully collected documentation for {len(successful)} tools:")
            for tool_name in successful:
                typer.echo(f"  • {tool_name}")
            
            if failed:
                typer.echo(f"\n❌ Failed to collect documentation for {len(failed)} tools:")
                for tool_name in failed:
                    typer.echo(f"  • {tool_name}")
            
            return
        
        if not tool:
            typer.echo("❌ Please specify a tool name or use --all to collect for all tools")
            typer.echo("Use --list to see available tools")
            raise typer.Exit(1)
        
        typer.echo(f"Collecting documentation for {tool}...")
        success = asyncio.run(collector.collect_documentation(tool, force_refresh))
        
        if success:
            typer.echo(f"✅ Successfully collected documentation for {tool}")
            typer.echo(f"📁 Documentation saved to: raw_docs/{tool}.md")
        else:
            typer.echo(f"❌ Failed to collect documentation for {tool}")
            typer.echo("Use --list to see available tools")
            raise typer.Exit(1)
            
    except ImportError as e:
        typer.echo(f"❌ Error importing collector: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error during collection: {e}")
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
        f"{indent}• {framework.name}{version_info}{source_info}{confidence_info}{tags_info}"
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