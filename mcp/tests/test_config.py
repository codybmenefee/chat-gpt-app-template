#!/usr/bin/env python3
"""
Test script for config_tools.py
Run this to verify Phase 1 configuration tools work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_tools import register_config_tools
from fastmcp import FastMCP

def test_config_tools():
    """Test all configuration tools."""
    print("Testing Configuration Tools...")
    print("=" * 50)
    
    # Import the individual functions directly
    from config_tools import config_get, config_set, config_status, config_reset
    
    # Test 1: config_get
    print("\n1. Testing config_get:")
    try:
        result = config_get()
        print("✅ config_get successful")
        print(f"Result preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ config_get failed: {e}")
    
    # Test 2: config_status
    print("\n2. Testing config_status:")
    try:
        result = config_status()
        print("✅ config_status successful")
        print(f"Result preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ config_status failed: {e}")
    
    # Test 3: config_set (with safe values)
    print("\n3. Testing config_set:")
    try:
        result = config_set(timeout=15000, retries=2)
        print("✅ config_set successful")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ config_set failed: {e}")
    
    # Test 4: config_reset
    print("\n4. Testing config_reset:")
    try:
        result = config_reset()
        print("✅ config_reset successful")
        print(f"Result preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ config_reset failed: {e}")
    
    print("\n" + "=" * 50)
    print("Phase 1 Testing Complete!")
    print("If all tests passed, Phase 1 is ready for ChatGPT testing.")

if __name__ == "__main__":
    test_config_tools()
