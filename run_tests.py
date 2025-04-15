#!/usr/bin/env python3
"""
Test Runner for IPL API

This script runs all tests for the IPL API to ensure it is working properly.
It runs both the Flask API tests and the IPL module function tests.
"""
import unittest
import sys
import time

def run_all_tests():
    """Run all test suites and return True if all pass"""
    # Start timing
    start_time = time.time()
    
    print("=" * 70)
    print("RUNNING IPL API TESTS")
    print("=" * 70)
    
    # Load test modules
    loader = unittest.TestLoader()
    
    # Create test suite containing all tests
    test_suite = unittest.TestSuite()
    
    # Add all tests from test_app.py and test_ipl.py
    test_suite.addTests(loader.discover('.', pattern='test_*.py'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Calculate and display execution time
    execution_time = time.time() - start_time
    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    
    # Display summary
    print("\nTEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # Return True if all tests passed
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_all_tests()
    # Set exit code based on test results
    sys.exit(0 if success else 1)