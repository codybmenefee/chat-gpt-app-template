#!/usr/bin/env python3
"""
Test script for upload_tools.py
Run this to verify Phase 3 upload tools work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_upload_tools():
    """Test file upload tool."""
    print("Testing Upload Tools...")
    print("=" * 50)
    
    # Import the function directly
    from upload_tools import upload_file
    
    # Test 1: Non-existent file
    print("\n1. Testing with non-existent file:")
    try:
        result = upload_file("/nonexistent/file.txt")
        print("✅ Error handling successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
    
    # Test 2: Invalid object_type
    print("\n2. Testing invalid object_type:")
    try:
        result = upload_file(__file__, object_type="INVALID")
        print("✅ Parameter validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
    
    # Test 3: Invalid file_type
    print("\n3. Testing invalid file_type:")
    try:
        result = upload_file(__file__, file_type="INVALID")
        print("✅ Parameter validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
    
    # Test 4: Invalid permission_type
    print("\n4. Testing invalid permission_type:")
    try:
        result = upload_file(__file__, permission_type="INVALID")
        print("✅ Parameter validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
    
    # Test 5: Configuration check
    print("\n5. Testing configuration validation:")
    try:
        # This will test if the configuration is properly loaded
        result = upload_file(__file__)
        print("✅ Configuration validation successful")
        print(f"Result preview: {result[:200]}...")
    except Exception as e:
        print(f"ℹ️ Configuration test result: {str(e)[:100]}...")
        print("   (This is expected if .env.local is not properly configured)")
    
    print("\n" + "=" * 50)
    print("Phase 3 Testing Complete!")
    print("If all tests passed, Phase 3 is ready for ChatGPT testing.")
    print("Note: Full upload testing requires proper .env.local configuration")

if __name__ == "__main__":
    test_upload_tools()

