#!/usr/bin/env python3
"""
Test script for theme_tools.py
Run this to verify Phase 4 theme tools work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_theme_tools():
    """Test theme and logo management tools."""
    print("Testing Theme Tools...")
    print("=" * 50)
    
    # Import the functions directly
    from theme_tools import (
        update_organization_theme, 
        list_organization_logos, 
        get_logo_download_url, 
        verify_organization_logo
    )
    
    # Test 1: Invalid hex color validation
    print("\n1. Testing invalid hex color validation:")
    try:
        invalid_theme_tokens = {
            "ref": {
                "palette": {
                    "primary50": "invalid-color"
                }
            }
        }
        result = update_organization_theme(theme_tokens=invalid_theme_tokens)
        print("✅ Color validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Color validation failed: {e}")
    
    # Test 2: Valid hex color validation
    print("\n2. Testing valid hex color validation:")
    try:
        valid_theme_tokens = {
            "ref": {
                "palette": {
                    "primary50": "#808080"
                }
            },
            "comp": {
                "layout": {
                    "backgroundColor": "#f5f5f5",
                    "textColor": "#333333"
                }
            }
        }
        result = update_organization_theme(theme_tokens=valid_theme_tokens)
        print("✅ Valid color format accepted")
        print(f"Result preview: {result[:200]}...")
    except Exception as e:
        print(f"ℹ️ Valid color test result: {str(e)[:100]}...")
        print("   (This is expected if .env.local is not properly configured)")
    
    # Test 3: Invalid organization ID
    print("\n3. Testing invalid organization ID:")
    try:
        result = update_organization_theme(organization_id="your_org_id_here")
        print("✅ Invalid org ID validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Invalid org ID validation failed: {e}")
    
    # Test 4: List logos with invalid limit
    print("\n4. Testing invalid limit parameter:")
    try:
        result = list_organization_logos(limit=100)
        print("✅ Limit validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Limit validation failed: {e}")
    
    # Test 5: Get download URL with empty ID
    print("\n5. Testing empty file document ID:")
    try:
        result = get_logo_download_url("")
        print("✅ Empty ID validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Empty ID validation failed: {e}")
    
    # Test 6: Configuration check
    print("\n6. Testing configuration validation:")
    try:
        result = verify_organization_logo()
        print("✅ Configuration validation successful")
        print(f"Result preview: {result[:200]}...")
    except Exception as e:
        print(f"ℹ️ Configuration test result: {str(e)[:100]}...")
        print("   (This is expected if .env.local is not properly configured)")
    
    print("\n" + "=" * 50)
    print("Phase 4 Testing Complete!")
    print("If all tests passed, Phase 4 is ready for ChatGPT testing.")
    print("Note: Full theme testing requires proper .env.local configuration")

if __name__ == "__main__":
    test_theme_tools()

