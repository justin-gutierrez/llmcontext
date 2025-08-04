"""
Tests for CLI functionality.
"""

import pytest
from click.testing import CliRunner
from llmcontext.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_help(runner):
    """Test that CLI help works."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "LLMContext" in result.output


def test_cli_version(runner):
    """Test that CLI version works."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_cli_status(runner):
    """Test that status command works."""
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "LLMContext Status:" in result.output


def test_cli_process_help(runner):
    """Test that process command help works."""
    result = runner.invoke(main, ["process", "--help"])
    assert result.exit_code == 0
    assert "Process a codebase" in result.output


def test_cli_server_help(runner):
    """Test that server command help works."""
    result = runner.invoke(main, ["server", "--help"])
    assert result.exit_code == 0
    assert "Start the FastAPI sidecar server" in result.output 