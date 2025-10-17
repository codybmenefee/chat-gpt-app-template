#!/usr/bin/env python3
"""
Test script for the hello world widget implementation.
Verifies proper MCP resource format and tool metadata.
"""

import os
import sys
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_widget_file_structure():
    """Test that the widget file exists and is properly structured."""
    print("🧪 Testing widget file structure...")
    
    widget_file = os.path.join(os.path.dirname(__file__), 'src', 'tools', 'ux_widget.py')
    
    if not os.path.exists(widget_file):
        print(f"❌ Widget file not found: {widget_file}")
        return False
    
    print(f"✅ Widget file exists: {widget_file}")
    
    # Check file size
    size = os.path.getsize(widget_file)
    print(f"📊 Widget file size: {size:,} bytes")
    
    return True

def test_widget_content():
    """Test that the widget file contains required elements."""
    print("\n🧪 Testing widget content...")
    
    widget_file = os.path.join(os.path.dirname(__file__), 'src', 'tools', 'ux_widget.py')
    
    try:
        with open(widget_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required elements
        checks = [
            ("FastMCP import", "from fastmcp import FastMCP" in content),
            ("Resource decorator", "@mcp.resource(" in content),
            ("Tool decorator", "@mcp.tool(" in content),
            ("UI URI", "ui://widget/hello-world.html" in content),
            ("MIME type", "text/html+skybridge" in content),
            ("Output template", "openai/outputTemplate" in content),
            ("HTML content", "<!DOCTYPE html>" in content),
            ("Root div", '<div class="container">' in content),
            ("JavaScript", "<script>" in content),
            ("Window OpenAI", "window.openai" in content)
        ]
        
        all_checks_pass = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name} - MISSING")
                all_checks_pass = False
        
        return all_checks_pass
        
    except Exception as e:
        print(f"❌ Error reading widget file: {e}")
        return False

def test_main_server_integration():
    """Test that main.py properly imports the widget."""
    print("\n🧪 Testing main server integration...")
    
    main_file = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper imports and registrations
        checks = [
            ("Widget import", "from tools.ux_widget import register_ux_widget_tools" in content),
            ("Widget registration", "register_ux_widget_tools(mcp)" in content),
            ("No old imports", "from tools.ux_tools import" not in content),
            ("No old registrations", "register_ux_tools(mcp)" not in content)
        ]
        
        all_checks_pass = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name} - MISSING")
                all_checks_pass = False
        
        return all_checks_pass
        
    except Exception as e:
        print(f"❌ Error reading main file: {e}")
        return False

def test_old_files_removed():
    """Test that old duplicate files have been removed."""
    print("\n🧪 Testing old files removal...")
    
    base_path = os.path.dirname(__file__)
    
    old_files = [
        "src/tools/ux_tools.py",
        "src/tools/ux_tools_simple.py",
        "test_ux_simple.py",
        "test_ux_component.py",
        "test_tool_direct.py",
        "test_mcp_server.py",
        "UX_COMPONENT_SUMMARY.md"
    ]
    
    all_removed = True
    for file_path in old_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"❌ Old file still exists: {file_path}")
            all_removed = False
        else:
            print(f"✅ Old file removed: {file_path}")
    
    return all_removed

if __name__ == "__main__":
    print("🚀 Hello World Widget Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_widget_file_structure),
        ("Widget Content", test_widget_content),
        ("Main Integration", test_main_server_integration),
        ("Old Files Removal", test_old_files_removed)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Hello World widget is ready for testing.")
        print("\nNext steps:")
        print("1. Start the MCP server: python src/main.py")
        print("2. Connect ChatGPT to http://127.0.0.1:8123/mcp")
        print("3. Call the hello_world_widget tool")
        print("4. Verify the widget renders inline in ChatGPT")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    exit(0 if all_passed else 1)
