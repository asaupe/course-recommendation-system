#!/usr/bin/env python3
"""
Test Runner for Course Recommendation System

Runs all unit tests and integration tests with proper reporting.
Provides options for different test levels and coverage reporting.
"""

import sys
import unittest
import argparse
import time
from pathlib import Path
from io import StringIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class TestResult:
    """Custom test result class for detailed reporting"""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.successes = []
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self):
        self.end_time = time.time()
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    @property
    def success_rate(self):
        if self.tests_run == 0:
            return 0
        return self.successes / self.tests_run


def discover_and_run_tests(test_pattern="test_*.py", verbosity=1):
    """Discover and run tests with custom reporting"""
    print("🧪 Course Recommendation System - Test Suite")
    print("=" * 60)
    
    # Discover tests
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=test_pattern)
    
    # Count total tests
    def count_tests(test_suite):
        count = 0
        for test in test_suite:
            if isinstance(test, unittest.TestSuite):
                count += count_tests(test)
            else:
                count += 1
        return count
    
    total_tests = count_tests(suite)
    print(f"📋 Discovered {total_tests} tests")
    
    # Run tests with custom result tracking
    result = TestResult()
    result.start_timer()
    
    # Capture test output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream, 
        verbosity=verbosity,
        buffer=True
    )
    
    test_result = runner.run(suite)
    result.end_timer()
    
    # Process results
    result.tests_run = test_result.testsRun
    result.failures = test_result.failures
    result.errors = test_result.errors
    result.skipped = test_result.skipped
    result.successes = result.tests_run - len(result.failures) - len(result.errors) - len(result.skipped)
    
    # Print summary
    print(f"\\n📊 Test Results Summary")
    print("=" * 30)
    print(f"🏃 Tests Run: {result.tests_run}")
    print(f"✅ Successes: {result.successes}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚨 Errors: {len(result.errors)}")
    print(f"⏭️ Skipped: {len(result.skipped)}")
    print(f"⏱️ Duration: {result.duration:.2f}s")
    print(f"📈 Success Rate: {result.success_rate:.1%}")
    
    # Print detailed failures/errors if any
    if result.failures:
        print(f"\\n❌ Test Failures ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"   {i}. {test}")
            if verbosity > 1:
                print(f"      {traceback.split(chr(10))[0]}")
    
    if result.errors:
        print(f"\\n🚨 Test Errors ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"   {i}. {test}")
            if verbosity > 1:
                print(f"      {traceback.split(chr(10))[0]}")
    
    if result.skipped:
        print(f"\\n⏭️ Skipped Tests ({len(result.skipped)}):")
        for i, (test, reason) in enumerate(result.skipped, 1):
            print(f"   {i}. {test}")
            if verbosity > 1 and reason:
                print(f"      Reason: {reason}")
    
    return result


def run_specific_test_module(module_name, verbosity=1):
    """Run tests from a specific module"""
    print(f"🎯 Running tests from: {module_name}")
    print("=" * 40)
    
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity,
            buffer=True
        )
        
        result = runner.run(suite)
        
        print(f"✅ Tests run: {result.testsRun}")
        print(f"❌ Failures: {len(result.failures)}")
        print(f"🚨 Errors: {len(result.errors)}")
        print(f"⏭️ Skipped: {len(result.skipped)}")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Error running {module_name}: {e}")
        return False


def run_test_categories():
    """Run tests by category"""
    categories = [
        ("Data Manager", "test_data_manager"),
        ("RAG System", "test_rag_system"),
        ("Embedding Search", "test_embedding_search"),
        ("Guardrails", "test_guardrails"),
        ("Integration", "test_integration")
    ]
    
    print("📂 Running Tests by Category")
    print("=" * 35)
    
    results = {}
    for category, module in categories:
        print(f"\\n🔍 Testing {category}...")
        success = run_specific_test_module(module, verbosity=0)
        results[category] = success
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}")
    
    print(f"\\n📋 Category Summary:")
    for category, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {category}")
    
    overall_success = all(results.values())
    return overall_success


def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔧 Checking Test Environment...")
    print("=" * 35)
    
    checks = []
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version >= (3, 8)
    checks.append(("Python Version", python_ok, f"{python_version.major}.{python_version.minor}"))
    
    # Check required modules
    required_modules = [
        "unittest",
        "json",
        "pathlib",
        "tempfile"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            checks.append((f"Module: {module}", True, "Available"))
        except ImportError:
            checks.append((f"Module: {module}", False, "Missing"))
    
    # Check optional modules
    optional_modules = [
        ("openai", "OpenAI integration"),
        ("chromadb", "RAG functionality"),
        ("faiss", "Embedding search"),
        ("pydantic", "Validation"),
        ("streamlit", "Frontend")
    ]
    
    for module, description in optional_modules:
        try:
            __import__(module)
            checks.append((f"{description}", True, "Available"))
        except ImportError:
            checks.append((f"{description}", False, "Optional - some tests will be skipped"))
    
    # Print results
    for check_name, passed, details in checks:
        status = "✅" if passed else "⚠️"
        print(f"   {status} {check_name}: {details}")
    
    critical_failures = [c for c in checks[:4] if not c[1]]  # First 4 are critical
    return len(critical_failures) == 0


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Course Recommendation System Test Runner")
    parser.add_argument("--verbose", "-v", action="count", default=1,
                       help="Increase verbosity (use -vv for extra verbose)")
    parser.add_argument("--module", "-m", type=str,
                       help="Run tests from specific module")
    parser.add_argument("--category", "-c", action="store_true",
                       help="Run tests by category")
    parser.add_argument("--check-env", action="store_true",
                       help="Check test environment only")
    parser.add_argument("--pattern", "-p", type=str, default="test_*.py",
                       help="Test file pattern (default: test_*.py)")
    
    args = parser.parse_args()
    
    # Check environment
    if args.check_env or not check_test_environment():
        if args.check_env:
            return 0
        print("\\n⚠️ Environment check failed. Some tests may not work properly.")
        print("   Continuing with available functionality...")
    
    print()  # Add spacing
    
    # Run specific test module
    if args.module:
        success = run_specific_test_module(args.module, args.verbose)
        return 0 if success else 1
    
    # Run by category
    if args.category:
        success = run_test_categories()
        return 0 if success else 1
    
    # Run all tests
    result = discover_and_run_tests(args.pattern, args.verbose)
    
    # Determine exit code
    if result.errors or result.failures:
        print("\\n❌ Some tests failed. Please review the results above.")
        return 1
    elif result.skipped == result.tests_run:
        print("\\n⚠️ All tests were skipped. Check your environment setup.")
        return 1
    else:
        print("\\n🎉 All available tests passed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
