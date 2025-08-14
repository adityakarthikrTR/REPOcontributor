#!/usr/bin/env python3
"""
Test script to verify all tools are working correctly
"""

import subprocess
import sys
import os

def run_command(cmd, description, expect_failure=False):
    """Run a command and return result"""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if expect_failure:
            # For GUI tools without tkinter, we expect them to fail gracefully
            if result.returncode != 0 and "tkinter is not available" in result.stdout:
                print("✅ SUCCESS (Expected graceful failure)")
                if result.stdout:
                    print("Output:")
                    print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
                return True
            else:
                print("❌ FAILED (Expected graceful failure but got different result)")
                return False
        else:
            if result.returncode == 0:
                print("✅ SUCCESS")
                if result.stdout:
                    print("Output:")
                    print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
                return True
            else:
                print("❌ FAILED")
                if result.stderr:
                    print("Error:")
                    print(result.stderr[:500])
                return False
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_tools():
    """Test all available tools"""
    print("🔍 Repository Contributor Analyzer - Tool Testing")
    print("=" * 60)
    
    # Test tkinter availability
    print("\n🖥️  Testing GUI Dependencies:")
    try:
        import tkinter
        print("✅ tkinter is available - GUI tools should work")
        gui_available = True
    except ImportError:
        print("❌ tkinter is NOT available - GUI tools will show helpful error messages")
        gui_available = False
    
    tests = []
    
    # Test command-line tools
    tests.append((
        [sys.executable, "repo_contributor_analyzer.py", "--help"],
        "Command-line analyzer help",
        False
    ))
    
    tests.append((
        [sys.executable, "repo_contributor_analyzer.py", "."],
        "Analyzing current repository",
        False
    ))
    
    # Test GUI tools (should show helpful error message if tkinter not available)
    if not gui_available:
        tests.append((
            [sys.executable, "tr_bulk_analyzer.py"],
            "GUI tool error handling (should show helpful message)",
            True
        ))
        
        tests.append((
            [sys.executable, "top_contributors_gui.py"],
            "GUI tool error handling (should show helpful message)",
            True
        ))
    
    # Run tests
    results = []
    for cmd, description, expect_failure in tests:
        success = run_command(cmd, description, expect_failure)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The tools are working correctly.")
        if not gui_available:
            print("💡 GUI tools provide helpful error messages when tkinter is not available.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_tools()
    sys.exit(0 if success else 1)