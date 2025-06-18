import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_conversation_parser import run_conversation_tests
from test_output_parser import test_output_parser
from test_linkedin_parser import run_linkedin_parser_tests
from test_linkedin_lookup_agent import run_linkedin_lookup_tests

def run_all_tests(include_api_tests: bool = False):
    """Run all test suites"""
    print("🚀 RUNNING ALL TEST SUITES")
    print("="*70)
    
    results = []
    
    try:
        # Test 1: Output Parser (no API calls)
        print("\n1️⃣ TESTING OUTPUT PARSER")
        print("-" * 40)
        results.append(test_output_parser())
        
        # Test 2: Ice Breaker (mock mode only by default)
        print("\n\n2️⃣ TESTING ICE BREAKER")
        print("-" * 40)
        results.append(run_linkedin_parser_tests(include_real_api=include_api_tests))
        
        # Test 3: LinkedIn Lookup Agent (basic tests)
        print("\n\n3️⃣ TESTING LINKEDIN LOOKUP AGENT")
        print("-" * 40)
        results.append(run_linkedin_lookup_tests(skip_api_tests=not include_api_tests))
        
        # Test 4: Conversation Parser (all tests)
        print("\n\n4️⃣ TESTING CONVERSATION PARSER")
        print("-" * 40)
        results.append(run_conversation_tests())
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*70)
        print("🎉 ALL TEST SUITES COMPLETED!")
        print("="*70)
        print(f"✅ Test Suites Passed: {passed}/{total}")
        
        if passed == total:
            print("🏆 ALL TESTS SUCCESSFUL!")
        else:
            print("⚠️ Some test suites had issues - check individual results above")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ Test suite runner failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_specific_test(test_suite: str, test_number: int = None, include_api: bool = False):
    """Run a specific test suite or test number"""
    if test_suite.lower() == "output":
        print("🧪 Running Output Parser Tests...")
        return test_output_parser()
    
    elif test_suite.lower() == "ice" or test_suite.lower() == "icebreaker":
        print("🧪 Running Ice Breaker Tests...")
        return run_linkedin_parser_tests(include_real_api=include_api)
    
    elif test_suite.lower() == "linkedin" or test_suite.lower() == "lookup":
        print("🧪 Running LinkedIn Lookup Agent Tests...")
        return run_linkedin_lookup_tests(skip_api_tests=not include_api)
    
    elif test_suite.lower() == "conversation":
        print(f"🧪 Running Conversation Parser Tests{f' (Test {test_number})' if test_number else ''}...")
        return run_conversation_tests(test_number)
    
    else:
        print("❌ Unknown test suite. Available options:")
        print("   'output' - Output Parser tests")
        print("   'ice' - Ice Breaker tests")
        print("   'linkedin' - LinkedIn Lookup Agent tests")
        print("   'conversation' - Conversation Parser tests")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    include_api = "--api" in sys.argv
    
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and "--api" in sys.argv):
        # No arguments (or just --api) - run all tests
        if include_api:
            print("Running all tests INCLUDING API calls...")
            print("⚠️ This will make real API requests and may consume credits!")
        else:
            print("Running all tests (mock/offline mode)...")
            print("Use --api flag to include real API tests")
        
        success = run_all_tests(include_api_tests=include_api)
        
    elif len(sys.argv) >= 2:
        # Specific test suite
        test_suite = sys.argv[1]
        test_number = None
        
        # Check for test number
        if len(sys.argv) >= 3 and sys.argv[2].isdigit():
            test_number = int(sys.argv[2])
        
        success = run_specific_test(test_suite, test_number, include_api)
        
    else:
        print("Usage:")
        print("  python run_all_tests.py                           # Run all tests (mock mode)")
        print("  python run_all_tests.py --api                     # Run all tests (including API calls)")
        print("  python run_all_tests.py output                    # Run output parser tests")
        print("  python run_all_tests.py ice                       # Run ice breaker tests")
        print("  python run_all_tests.py ice --api                 # Run ice breaker tests with real API")
        print("  python run_all_tests.py linkedin                  # Run LinkedIn agent tests")
        print("  python run_all_tests.py linkedin --api            # Run LinkedIn agent tests with API")
        print("  python run_all_tests.py conversation              # Run all conversation tests")
        print("  python run_all_tests.py conversation 3            # Run conversation test 3")
        sys.exit(1)
    
    sys.exit(0 if success else 1)