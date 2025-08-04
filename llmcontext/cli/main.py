"""
Main CLI application using Typer.
"""

import json
import typer
from pathlib import Path
from typing import Optional, List
from enum import Enum

app = typer.Typer(
    name="llmcontext",
    help="Universal sidecar service + CLI for framework detection and documentation optimization",
    add_completion=False,
)


class Tool(str, Enum):
    """Supported tools/frameworks."""
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
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    TERRAFORM = "terraform"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


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
    
    typer.echo("🔍 Scanning codebase for configured frameworks...")
    # TODO: Implement actual framework detection
    typer.echo("⚠️  Framework detection not yet implemented.")
    typer.echo("This will be implemented in future iterations.")


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