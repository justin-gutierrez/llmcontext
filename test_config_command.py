#!/usr/bin/env python3
"""
Test script for the config command.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llmcontext.config import get_model_config, update_model_config


def run_cli_command(args: list) -> tuple:
    """
    Run a CLI command and return the result.
    
    Args:
        args: List of command arguments
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["python", "-m", "llmcontext.cli.main"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_config_show():
    """Test the config --show command."""
    print("=== Testing config --show ===\n")
    
    return_code, stdout, stderr = run_cli_command(["config", "--show"])
    
    print(f"Return code: {return_code}")
    print(f"Stdout:\n{stdout}")
    if stderr:
        print(f"Stderr:\n{stderr}")
    
    if return_code == 0 and "Current configuration:" in stdout:
        print("✅ config --show PASSED")
        return True
    else:
        print("❌ config --show FAILED")
        return False


def test_config_list_providers():
    """Test the config --list-providers command."""
    print("\n=== Testing config --list-providers ===\n")
    
    return_code, stdout, stderr = run_cli_command(["config", "--list-providers"])
    
    print(f"Return code: {return_code}")
    print(f"Stdout:\n{stdout}")
    if stderr:
        print(f"Stderr:\n{stderr}")
    
    if return_code == 0 and "Supported providers:" in stdout and "openai" in stdout and "ollama" in stdout:
        print("✅ config --list-providers PASSED")
        return True
    else:
        print("❌ config --list-providers FAILED")
        return False


def test_config_set_provider():
    """Test setting the provider and model."""
    print("\n=== Testing config --provider --model ===\n")
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Test setting to ollama/mistral
        return_code, stdout, stderr = run_cli_command(["config", "--provider", "ollama", "--model", "mistral"])
        
        print(f"Return code: {return_code}")
        print(f"Stdout:\n{stdout}")
        if stderr:
            print(f"Stderr:\n{stderr}")
        
        if return_code == 0 and "SUCCESS: Configuration updated" in stdout:
            print("✅ config --provider ollama --model mistral PASSED")
            
            # Verify the change was actually made
            new_config = get_model_config()
            if new_config["provider"] == "ollama" and new_config["model"] == "mistral":
                print("✅ Configuration change verified")
                success = True
            else:
                print("❌ Configuration change not verified")
                success = False
        else:
            print("❌ config --provider ollama --model mistral FAILED")
            success = False
        
        return success
        
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_config_set_provider_only():
    """Test setting only the provider."""
    print("\n=== Testing config --provider only ===\n")
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Test setting only provider
        return_code, stdout, stderr = run_cli_command(["config", "--provider", "openai"])
        
        print(f"Return code: {return_code}")
        print(f"Stdout:\n{stdout}")
        if stderr:
            print(f"Stderr:\n{stderr}")
        
        if return_code == 0 and "SUCCESS: Configuration updated" in stdout:
            print("✅ config --provider openai PASSED")
            
            # Verify the change was actually made
            new_config = get_model_config()
            if new_config["provider"] == "openai" and new_config["model"] == current_config["model"]:
                print("✅ Configuration change verified (model unchanged)")
                success = True
            else:
                print("❌ Configuration change not verified")
                success = False
        else:
            print("❌ config --provider openai FAILED")
            success = False
        
        return success
        
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_config_set_model_only():
    """Test setting only the model."""
    print("\n=== Testing config --model only ===\n")
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Test setting only model
        return_code, stdout, stderr = run_cli_command(["config", "--model", "llama2"])
        
        print(f"Return code: {return_code}")
        print(f"Stdout:\n{stdout}")
        if stderr:
            print(f"Stderr:\n{stderr}")
        
        if return_code == 0 and "SUCCESS: Configuration updated" in stdout:
            print("✅ config --model llama2 PASSED")
            
            # Verify the change was actually made
            new_config = get_model_config()
            if new_config["model"] == "llama2" and new_config["provider"] == current_config["provider"]:
                print("✅ Configuration change verified (provider unchanged)")
                success = True
            else:
                print("❌ Configuration change not verified")
                success = False
        else:
            print("❌ config --model llama2 FAILED")
            success = False
        
        return success
        
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_config_no_args():
    """Test config command with no arguments."""
    print("\n=== Testing config with no arguments ===\n")
    
    return_code, stdout, stderr = run_cli_command(["config"])
    
    print(f"Return code: {return_code}")
    print(f"Stdout:\n{stdout}")
    if stderr:
        print(f"Stderr:\n{stderr}")
    
    if return_code != 0 and "ERROR: Must specify either --provider or --model" in stdout:
        print("✅ config with no args correctly shows error")
        return True
    else:
        print("❌ config with no args should show error")
        return False


def test_config_help():
    """Test config command help."""
    print("\n=== Testing config --help ===\n")
    
    return_code, stdout, stderr = run_cli_command(["config", "--help"])
    
    print(f"Return code: {return_code}")
    print(f"Stdout:\n{stdout}")
    if stderr:
        print(f"Stderr:\n{stderr}")
    
    if return_code == 0 and "Configure model provider and model settings" in stdout:
        print("✅ config --help PASSED")
        return True
    else:
        print("❌ config --help FAILED")
        return False


if __name__ == "__main__":
    print("=== Config Command Test Suite ===\n")
    
    tests = [
        ("Config Show", test_config_show),
        ("Config List Providers", test_config_list_providers),
        ("Config Set Provider and Model", test_config_set_provider),
        ("Config Set Provider Only", test_config_set_provider_only),
        ("Config Set Model Only", test_config_set_model_only),
        ("Config No Args", test_config_no_args),
        ("Config Help", test_config_help)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED\n")
        else:
            print(f"❌ {test_name} FAILED\n")
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests PASSED! Config command is working correctly.")
    else:
        print("❌ Some tests FAILED. Please check the implementation.")
        sys.exit(1) 