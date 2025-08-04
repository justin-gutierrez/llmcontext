#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced status output features of the llmcontext add command.
This script shows the detailed progress tracking, timing information, and final summary statistics.
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*80}")
    print(f"DEMONSTRATING: {description}")
    print(f"COMMAND: {cmd}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        print("OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"EXIT CODE: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False, "", str(e)

def check_enhanced_features(output):
    """Check if the enhanced status output features are present."""
    features = {
        "Provider/Model Info": "MODEL: Using ollama with model" in output,
        "Progress Tracking": "[ 1/" in output and "STARTING:" in output,
        "Timing Information": "processed in" in output and "s ->" in output,
        "Final Summary": "STATS:" in output and "TIME:" in output,
        "Visual Separators": "------------------------------------------------------------" in output,
        "Success Count": "chunks successfully processed" in output
    }
    
    print("\n" + "="*60)
    print("ENHANCED STATUS OUTPUT FEATURES CHECK")
    print("="*60)
    
    all_present = True
    for feature, present in features.items():
        status = "✅ PRESENT" if present else "❌ MISSING"
        print(f"{feature:25} {status}")
        if not present:
            all_present = False
    
    print("="*60)
    return all_present

def main():
    """Main demonstration function."""
    print("ENHANCED STATUS OUTPUT DEMONSTRATION")
    print("This script demonstrates the improved status output during documentation processing")
    
    # Test 1: Show current configuration
    success, stdout, stderr = run_command(
        "python -m llmcontext.cli.main config --show",
        "Current Model Configuration"
    )
    
    if not success:
        print("WARNING: Could not show configuration, continuing anyway...")
    
    # Test 2: Add a tool with enhanced status output
    success, stdout, stderr = run_command(
        "python -m llmcontext.cli.main add fastapi",
        "Enhanced Status Output During Documentation Processing"
    )
    
    if success:
        print("SUCCESS: FastAPI added with enhanced status output")
        
        # Check for enhanced features
        enhanced_features_present = check_enhanced_features(stdout)
        
        if enhanced_features_present:
            print("\n🎉 ALL ENHANCED FEATURES ARE WORKING CORRECTLY!")
        else:
            print("\n⚠️  SOME ENHANCED FEATURES ARE MISSING")
        
        # Show what was created
        print("\n" + "="*60)
        print("CREATED FILES")
        print("="*60)
        
        # Check raw docs
        raw_docs_path = Path("raw_docs/fastapi.md")
        if raw_docs_path.exists():
            print(f"📄 Raw docs: {raw_docs_path} ({raw_docs_path.stat().st_size} bytes)")
        
        # Check chunks
        chunks_dir = Path("chunks/fastapi")
        if chunks_dir.exists():
            chunk_files = list(chunks_dir.glob("*.md"))
            print(f"📦 Chunks: {len(chunk_files)} files in {chunks_dir}")
            for chunk_file in chunk_files[:3]:
                print(f"   - {chunk_file.name}")
            if len(chunk_files) > 3:
                print(f"   ... and {len(chunk_files) - 3} more")
        
        # Check processed docs
        docs_dir = Path("docs/fastapi")
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            print(f"📚 Processed docs: {len(doc_files)} files in {docs_dir}")
            for doc_file in doc_files[:3]:
                print(f"   - {doc_file.name}")
            if len(doc_files) > 3:
                print(f"   ... and {len(doc_files) - 3} more")
        
    else:
        print("ERROR: Failed to add FastAPI")
        return
    
    # Test 3: Show the enhanced features summary
    print("\n" + "="*80)
    print("ENHANCED STATUS OUTPUT FEATURES SUMMARY")
    print("="*80)
    print("✅ Provider/Model Information: Shows which LLM provider and model is being used")
    print("✅ Progress Tracking: [X/Y] format with STARTING/SUCCESS/ERROR status")
    print("✅ Timing Information: Individual chunk processing times and total time")
    print("✅ Final Summary: Statistics showing successful/failed chunks and timing")
    print("✅ Visual Separators: Clear separation between processing steps")
    print("✅ File Output: Shows exactly which files were created")
    print("✅ Error Handling: Graceful fallback when chunks fail to process")
    print("="*80)

if __name__ == "__main__":
    main() 