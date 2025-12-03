"""
Test script for Results Storage System
Tests the ResultsManager and verifies that scraping results are saved correctly.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.results_manager import ResultsManager


def test_results_manager():
    """Test the ResultsManager functionality."""
    print("="*60)
    print("TEST: Results Manager")
    print("="*60)
    
    # Initialize ResultsManager
    print("\n1. Initializing ResultsManager...")
    rm = ResultsManager()
    print(f"   ✓ Results directory: {rm.results_dir}")
    
    # Verify directory exists
    if os.path.exists(rm.results_dir):
        print(f"   ✓ Directory exists")
    else:
        print(f"   ✗ Directory does not exist!")
        return False
    
    # Test saving a result
    print("\n2. Testing save_result()...")
    test_data = {
        "assistant_id": "test_123",
        "assistant_name": "Test Assistant",
        "url": "https://example.com",
        "query": "test query",
        "extraction_prompt": "Extract test data",
        "results": "Test results formatted",
        "raw_results": {"test": "data"},
        "provider": "openai",
        "model": "gpt-4o-mini"
    }
    
    filepath = rm.save_result(test_data)
    print(f"   ✓ Saved to: {filepath}")
    
    # Verify file exists
    if os.path.exists(filepath):
        print(f"   ✓ File exists")
    else:
        print(f"   ✗ File does not exist!")
        return False
    
    # Test loading the result
    print("\n3. Testing load_result()...")
    loaded_data = rm.load_result(filepath)
    
    if loaded_data:
        print(f"   ✓ Loaded successfully")
        print(f"   - Assistant: {loaded_data.get('assistant_name')}")
        print(f"   - Query: {loaded_data.get('query')}")
        print(f"   - Timestamp: {loaded_data.get('timestamp')}")
    else:
        print(f"   ✗ Failed to load!")
        return False
    
    # Verify data integrity
    if loaded_data.get('query') == test_data['query']:
        print(f"   ✓ Data integrity verified")
    else:
        print(f"   ✗ Data mismatch!")
        return False
    
    # Test get_recent_results
    print("\n4. Testing get_recent_results()...")
    recent = rm.get_recent_results("test_123", limit=5)
    print(f"   ✓ Found {len(recent)} recent result(s)")
    
    if len(recent) > 0:
        print(f"   ✓ Most recent query: {recent[0].get('query')}")
    
    # Test get_results_summary
    print("\n5. Testing get_results_summary()...")
    summary = rm.get_results_summary("test_123")
    print(f"   ✓ Total count: {summary['total_count']}")
    print(f"   ✓ Most recent: {summary['most_recent']}")
    
    # Display file content
    print("\n6. Displaying saved file content...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
        print(f"   File: {os.path.basename(filepath)}")
        print(f"   Size: {os.path.getsize(filepath)} bytes")
        print(f"   Keys: {list(content.keys())}")
    
    print("\n" + "="*60)
    print("✓✓✓ ALL TESTS PASSED!")
    print("="*60)
    
    return True


def test_directory_structure():
    """Test that the directory structure is correct."""
    print("\n" + "="*60)
    print("TEST: Directory Structure")
    print("="*60)
    
    rm = ResultsManager()
    
    print(f"\nResults directory: {rm.results_dir}")
    
    if os.path.exists(rm.results_dir):
        files = os.listdir(rm.results_dir)
        print(f"Files in directory: {len(files)}")
        
        if files:
            print("\nRecent files:")
            for f in sorted(files, reverse=True)[:5]:
                filepath = os.path.join(rm.results_dir, f)
                size = os.path.getsize(filepath)
                print(f"  - {f} ({size} bytes)")
        else:
            print("  (empty)")
    else:
        print("  ✗ Directory does not exist!")
        return False
    
    return True


if __name__ == "__main__":
    print("\n🧪 Starting Results Storage Tests...\n")
    
    # Run tests
    test1_passed = test_results_manager()
    test2_passed = test_directory_structure()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Results Manager Test: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Directory Structure Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("\nThe results storage system is working correctly.")
        print("You can now use the application and scraping results will be saved.")
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease check the errors above.")
