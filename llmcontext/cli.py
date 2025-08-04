"""
CLI entry point for LLMContext.
"""

import click
import uvicorn
from pathlib import Path

from .api import app


@click.group()
@click.version_option()
def main():
    """
    LLMContext - Universal sidecar service + CLI for framework detection and documentation optimization.
    
    This tool detects frameworks/libraries in your codebase, collects and compresses their documentation
    using an LLM, tags and embeds the results, and serves optimized, RAG-ready context.
    """
    pass


@main.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the server to",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to bind the server to",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload on code changes",
)
def server(host: str, port: int, reload: bool):
    """Start the FastAPI sidecar server."""
    click.echo(f"Starting LLMContext server on {host}:{port}")
    uvicorn.run(
        "llmcontext.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@main.command()
@click.argument("codebase_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("docs"),
    help="Output directory for processed documentation",
    show_default=True,
)
def process(codebase_path: Path, output: Path):
    """Process a codebase to detect frameworks and collect documentation."""
    click.echo(f"Processing codebase: {codebase_path}")
    click.echo(f"Output directory: {output}")
    
    # TODO: Implement framework detection and documentation collection
    click.echo("Framework detection and documentation collection not yet implemented.")
    click.echo("This will be implemented in future iterations.")


@main.command()
def status():
    """Show the current status of the LLMContext service."""
    click.echo("LLMContext Status:")
    click.echo("  - Service: Not running")
    click.echo("  - Documentation cache: Empty")
    click.echo("  - Framework detection: Ready")
    click.echo("  - API endpoints: Available")


if __name__ == "__main__":
    main() 