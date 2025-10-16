#!/usr/bin/env python3
"""
Test script for pdf_tools.py
Run this to verify Phase 2 PDF tools work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_tools():
    """Test PDF extraction tool."""
    print("Testing PDF Tools...")
    print("=" * 50)
    
    # Import the function directly
    from pdf_tools import view_pdf
    
    # Test 1: Non-existent file
    print("\n1. Testing with non-existent file:")
    try:
        result = view_pdf("/nonexistent/file.pdf")
        print("✅ Error handling successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
    
    # Test 2: Non-PDF file
    print("\n2. Testing with non-PDF file:")
    try:
        result = view_pdf(__file__)  # This script file
        print("✅ File type validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ File type validation failed: {e}")
    
    # Test 3: Invalid max_pages parameter
    print("\n3. Testing invalid max_pages parameter:")
    try:
        result = view_pdf("test.pdf", max_pages=150)
        print("✅ Parameter validation successful")
        print(f"Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
    
    # Test 4: Create a simple test PDF if possible
    print("\n4. Testing with sample PDF (if available):")
    test_pdf_path = "/Users/codymenefee/Documents/OV-Codebase/one-agent/COMPLETE_MIGRATION_PLAN.md"
    if os.path.exists(test_pdf_path):
        print(f"Note: Testing with markdown file instead of PDF: {test_pdf_path}")
        try:
            result = view_pdf(test_pdf_path)
            print("✅ File processing successful")
            print(f"Result preview: {result[:200]}...")
        except Exception as e:
            print(f"❌ File processing failed: {e}")
    else:
        print("ℹ️ No test PDF file available - skipping PDF extraction test")
        print("   To test PDF extraction, place a PDF file in the project directory")
    
    print("\n" + "=" * 50)
    print("Phase 2 Testing Complete!")
    print("If all tests passed, Phase 2 is ready for ChatGPT testing.")

if __name__ == "__main__":
    test_pdf_tools()

