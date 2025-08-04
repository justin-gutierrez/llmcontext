#!/usr/bin/env python3
"""
Development setup script for LLMContext.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("Setting up LLMContext development environment...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install the package in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command("pip install -e .[dev]", "Installing development dependencies"):
        sys.exit(1)
    
    # Create docs directory if it doesn't exist
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    print("✓ Created docs directory")
    
    # Run tests to verify installation
    if not run_command("pytest tests/ -v", "Running tests"):
        print("Warning: Tests failed, but setup completed")
    
    print("\n🎉 LLMContext development environment setup complete!")
    print("\nNext steps:")
    print("1. Run 'llmcontext --help' to see available commands")
    print("2. Run 'llmcontext init' to initialize a new project")
    print("3. Run 'llmcontext add react' to add a framework")
    print("4. Run 'llmcontext server' to start the API server")
    print("5. Run 'pytest' to run the test suite")
    print("6. Check out the README.md for more information")


if __name__ == "__main__":
    main() 