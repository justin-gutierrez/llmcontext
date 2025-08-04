#!/usr/bin/env python3
"""
Test script for configuration management.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llmcontext.config import (
    get_config, 
    get_model_config, 
    update_model_config,
    get_stack,
    add_to_stack,
    remove_from_stack,
    validate_config,
    create_default_config
)


def test_config_loading():
    """Test loading the current configuration."""
    print("=== Configuration Loading Test ===\n")
    
    try:
        config = get_config()
        print("SUCCESS: Configuration loaded successfully")
        print(f"Full config: {config}")
        
        # Test model configuration
        model_config = get_model_config()
        print(f"\nModel config: {model_config}")
        print(f"Provider: {model_config['provider']}")
        print(f"Model: {model_config['model']}")
        
        # Test stack
        stack = get_stack()
        print(f"\nStack: {stack}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        return False


def test_model_config_update():
    """Test updating model configuration."""
    print("\n=== Model Configuration Update Test ===\n")
    
    try:
        # Get current config
        current_config = get_model_config()
        print(f"Current model config: {current_config}")
        
        # Update to different provider/model
        new_provider = "ollama"
        new_model = "llama2"
        
        print(f"Updating to: {new_provider}/{new_model}")
        update_model_config(new_provider, new_model)
        
        # Verify update
        updated_config = get_model_config()
        print(f"Updated model config: {updated_config}")
        
        if updated_config["provider"] == new_provider and updated_config["model"] == new_model:
            print("SUCCESS: Model configuration updated correctly")
            
            # Restore original config
            print("Restoring original config...")
            update_model_config(current_config["provider"], current_config["model"])
            print("SUCCESS: Original config restored")
            return True
        else:
            print("ERROR: Model configuration not updated correctly")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to update model configuration: {e}")
        return False


def test_stack_operations():
    """Test stack operations."""
    print("\n=== Stack Operations Test ===\n")
    
    try:
        # Get current stack
        current_stack = get_stack()
        print(f"Current stack: {current_stack}")
        
        # Add a test tool
        test_tool = "test-tool@1.0"
        print(f"Adding tool: {test_tool}")
        add_to_stack(test_tool)
        
        # Verify addition
        updated_stack = get_stack()
        print(f"Stack after addition: {updated_stack}")
        
        if test_tool in updated_stack:
            print("SUCCESS: Tool added to stack")
        else:
            print("ERROR: Tool not added to stack")
            return False
        
        # Remove the test tool
        print(f"Removing tool: {test_tool}")
        remove_from_stack(test_tool)
        
        # Verify removal
        final_stack = get_stack()
        print(f"Stack after removal: {final_stack}")
        
        if test_tool not in final_stack:
            print("SUCCESS: Tool removed from stack")
            return True
        else:
            print("ERROR: Tool not removed from stack")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to perform stack operations: {e}")
        return False


def test_config_validation():
    """Test configuration validation."""
    print("\n=== Configuration Validation Test ===\n")
    
    try:
        # Test valid config
        valid_config = {
            "stack": ["react@18", "tailwind@3.3"],
            "model_provider": "ollama",
            "model_name": "mistral"
        }
        
        is_valid = validate_config(valid_config)
        print(f"Valid config test: {is_valid}")
        
        if not is_valid:
            print("ERROR: Valid config failed validation")
            return False
        
        # Test invalid config (missing stack)
        invalid_config = {
            "model_provider": "ollama",
            "model_name": "mistral"
        }
        
        is_invalid = not validate_config(invalid_config)
        print(f"Invalid config test: {is_invalid}")
        
        if not is_invalid:
            print("ERROR: Invalid config passed validation")
            return False
        
        # Test invalid config (wrong stack type)
        invalid_config2 = {
            "stack": "not-a-list",
            "model_provider": "ollama"
        }
        
        is_invalid2 = not validate_config(invalid_config2)
        print(f"Invalid config type test: {is_invalid2}")
        
        if not is_invalid2:
            print("ERROR: Invalid config type passed validation")
            return False
        
        print("SUCCESS: All validation tests passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Validation test failed: {e}")
        return False


def test_default_config():
    """Test default configuration creation."""
    print("\n=== Default Configuration Test ===\n")
    
    try:
        default_config = create_default_config()
        print(f"Default config: {default_config}")
        
        # Verify structure
        required_keys = ["stack", "model_provider", "model_name"]
        for key in required_keys:
            if key not in default_config:
                print(f"ERROR: Missing key in default config: {key}")
                return False
        
        # Verify types
        if not isinstance(default_config["stack"], list):
            print("ERROR: Stack should be a list")
            return False
        
        if not isinstance(default_config["model_provider"], str):
            print("ERROR: model_provider should be a string")
            return False
        
        if not isinstance(default_config["model_name"], str):
            print("ERROR: model_name should be a string")
            return False
        
        print("SUCCESS: Default configuration is valid")
        return True
        
    except Exception as e:
        print(f"ERROR: Default config test failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Configuration Management Test Suite ===\n")
    
    tests = [
        ("Config Loading", test_config_loading),
        ("Model Config Update", test_model_config_update),
        ("Stack Operations", test_stack_operations),
        ("Config Validation", test_config_validation),
        ("Default Config", test_default_config)
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
        print("🎉 All tests PASSED! Configuration management is working correctly.")
    else:
        print("❌ Some tests FAILED. Please check the configuration.")
        sys.exit(1) 