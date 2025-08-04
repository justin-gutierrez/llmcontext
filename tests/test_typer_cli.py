"""
Tests for Typer CLI functionality.
"""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner
from llmcontext.cli.main import app, get_config_path


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


def test_cli_help(runner):
    """Test that CLI help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "llmcontext" in result.output
    assert "Universal sidecar service" in result.output


def test_init_command(runner, temp_dir, monkeypatch):
    """Test the init command."""
    monkeypatch.chdir(temp_dir)
    
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Created configuration file" in result.output
    
    config_path = temp_dir / ".llmcontext.json"
    assert config_path.exists()
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    assert config["version"] == "1.0.0"
    assert "project" in config
    assert "settings" in config
    assert "api" in config
    assert "tools" in config


def test_init_command_force(runner, temp_dir, monkeypatch):
    """Test the init command with force flag."""
    monkeypatch.chdir(temp_dir)
    
    # Create initial config
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    
    # Try to init again without force
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "already exists" in result.output
    
    # Try with force
    result = runner.invoke(app, ["init", "--force"])
    assert result.exit_code == 0
    assert "Created configuration file" in result.output


def test_add_command_no_config(runner, temp_dir, monkeypatch):
    """Test add command without config file."""
    monkeypatch.chdir(temp_dir)
    
    result = runner.invoke(app, ["add", "react"])
    assert result.exit_code == 1
    assert "Configuration file not found" in result.output


def test_add_command(runner, temp_dir, monkeypatch):
    """Test the add command."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Add a tool
    result = runner.invoke(app, ["add", "react"])
    assert result.exit_code == 0
    assert "Added 'react' to configuration" in result.output
    
    # Check config file
    config_path = temp_dir / ".llmcontext.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    assert "react" in config["tools"]["enabled"]
    assert "react" in config["tools"]["tool_configs"]


def test_add_command_with_version(runner, temp_dir, monkeypatch):
    """Test add command with version."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Add a tool with version
    result = runner.invoke(app, ["add", "react", "--version", "18.2.0"])
    assert result.exit_code == 0
    assert "Added 'react' to configuration" in result.output
    assert "Tracking version: 18.2.0" in result.output
    
    # Check config file
    config_path = temp_dir / ".llmcontext.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    assert config["tools"]["tool_configs"]["react"]["version"] == "18.2.0"


def test_add_command_duplicate(runner, temp_dir, monkeypatch):
    """Test adding the same tool twice."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Add a tool
    runner.invoke(app, ["add", "react"])
    
    # Try to add the same tool again
    result = runner.invoke(app, ["add", "react"])
    assert result.exit_code == 0
    assert "already enabled" in result.output


def test_remove_command(runner, temp_dir, monkeypatch):
    """Test the remove command."""
    monkeypatch.chdir(temp_dir)
    
    # First init and add a tool
    runner.invoke(app, ["init"])
    runner.invoke(app, ["add", "react"])
    
    # Remove the tool
    result = runner.invoke(app, ["remove", "react"])
    assert result.exit_code == 0
    assert "Removed 'react' from configuration" in result.output
    
    # Check config file
    config_path = temp_dir / ".llmcontext.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    assert "react" not in config["tools"]["enabled"]
    assert "react" not in config["tools"]["tool_configs"]


def test_remove_command_not_enabled(runner, temp_dir, monkeypatch):
    """Test removing a tool that's not enabled."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Try to remove a tool that's not enabled
    result = runner.invoke(app, ["remove", "react"])
    assert result.exit_code == 0
    assert "not enabled" in result.output


def test_list_tools_command(runner, temp_dir, monkeypatch):
    """Test the list-tools command."""
    monkeypatch.chdir(temp_dir)
    
    # First init and add tools
    runner.invoke(app, ["init"])
    runner.invoke(app, ["add", "react"])
    runner.invoke(app, ["add", "tailwind"])
    
    # List tools
    result = runner.invoke(app, ["list-tools"])
    assert result.exit_code == 0
    assert "Configured tools:" in result.output
    assert "react" in result.output
    assert "tailwind" in result.output


def test_list_tools_command_no_tools(runner, temp_dir, monkeypatch):
    """Test list-tools command with no tools configured."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # List tools
    result = runner.invoke(app, ["list-tools"])
    assert result.exit_code == 0
    assert "No tools configured" in result.output


def test_detect_command(runner, temp_dir, monkeypatch):
    """Test the detect command."""
    monkeypatch.chdir(temp_dir)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Run detect
    result = runner.invoke(app, ["detect"])
    assert result.exit_code == 0
    assert "Scanning codebase" in result.output
    assert "not yet implemented" in result.output


def test_get_default_patterns():
    """Test getting default patterns for tools."""
    from llmcontext.cli.main import get_default_patterns, Tool
    
    patterns = get_default_patterns(Tool.REACT)
    assert "package.json" in patterns
    assert "src/**/*.jsx" in patterns
    assert "src/**/*.tsx" in patterns
    
    patterns = get_default_patterns(Tool.TAILWIND)
    assert "tailwind.config.js" in patterns
    assert "**/*.css" in patterns


def test_get_documentation_sources():
    """Test getting documentation sources for tools."""
    from llmcontext.cli.main import get_documentation_sources, Tool
    
    sources = get_documentation_sources(Tool.REACT)
    assert "https://react.dev" in sources
    
    sources = get_documentation_sources(Tool.FASTAPI)
    assert "https://fastapi.tiangolo.com" in sources 