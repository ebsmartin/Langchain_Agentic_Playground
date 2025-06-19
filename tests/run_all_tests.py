import sys
import os
import io
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_conversation_parser import run_conversation_tests
from test_output_parser import test_output_parser
from test_linkedin_parser import run_linkedin_parser_tests
from test_linkedin_lookup_agent import run_linkedin_lookup_tests
from utils.output_manager import output_manager

class TeeOutput:
    """Captures output to both console and a string buffer"""
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.buffer = io.StringIO()
    
    def write(self, text):
        # Write to both console and buffer
        self.original_stream.write(text)
        self.buffer.write(text)
        return len(text)
    
    def flush(self):
        self.original_stream.flush()
        self.buffer.flush()
    
    def getvalue(self):
        return self.buffer.getvalue()

def save_test_output(output_content: str, test_type: str = "all", test_number: int = None):
    """Save test output to a timestamped file in the output folder"""
    # Create output folder if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if test_number:
        filename = f"test_output_{test_type}_{test_number}_{timestamp}.txt"
    else:
        filename = f"test_output_{test_type}_{timestamp}.txt"
    
    filepath = os.path.join(output_dir, filename)
    
    # Add header with test info
    header = f"""
{'='*80}
TEST OUTPUT LOG
{'='*80}
Test Type: {test_type.upper()}
{f'Test Number: {test_number}' if test_number else 'All Tests'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System: {sys.platform}
Python: {sys.version.split()[0]}
{'='*80}

"""
    
    # Save to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(output_content)
        
        print(f"\n📄 Test output saved to: {filename}")
        return filename
    except Exception as e:
        print(f"\n⚠️ Failed to save test output: {e}")
        return None

def run_all_tests(include_api_tests: bool = False):
    """Run all test suites and capture output"""
    # Capture both stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    stdout_capture = TeeOutput(original_stdout)
    stderr_capture = TeeOutput(original_stderr)
    
    try:
        # Redirect output to capture
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        print("🚀 RUNNING ALL TEST SUITES")
        print("="*70)
        
        results = []
        
        # Test 1: Output Parser (no API calls)
        print("\n1️⃣ TESTING OUTPUT PARSER")
        print("-" * 40)
        output_result = test_output_parser()
        results.append(output_result if output_result is not None else False)
        
        # Test 2: Ice Breaker (mock mode only by default)
        print("\n\n2️⃣ TESTING ICE BREAKER")
        print("-" * 40)
        ice_result = run_linkedin_parser_tests(include_real_api=include_api_tests)
        results.append(ice_result if ice_result is not None else False)
        
        # Test 3: LinkedIn Lookup Agent (basic tests)
        print("\n\n3️⃣ TESTING LINKEDIN LOOKUP AGENT")
        print("-" * 40)
        linkedin_result = run_linkedin_lookup_tests(skip_api_tests=not include_api_tests)
        results.append(linkedin_result if linkedin_result is not None else False)
        
        # Test 4: Conversation Parser (all tests)
        print("\n\n4️⃣ TESTING CONVERSATION PARSER")
        print("-" * 40)
        conversation_result = run_conversation_tests()
        results.append(conversation_result if conversation_result is not None else False)
        
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
        
        # Show saved output files if any were created
        print("\n📁 CHECKING FOR SAVED OUTPUT FILES...")
        saved_analyses = output_manager.list_saved_analyses()
        if saved_analyses:
            print(f"Found {len(saved_analyses)} saved conversation analyses:")
            for analysis in saved_analyses[-5:]:  # Show last 5
                print(f"   📄 {analysis.get('person_name', 'Unknown')} ({analysis.get('filename', '')})")
            print(f"\n💡 Use 'python conversation_parser.py --view' to see all saved analyses")
            print(f"💡 Use 'python utils/results_viewer.py' for interactive viewing")
        else:
            print("No output files were saved (this is normal for mock tests)")
        
        success = passed == total
        
    except Exception as e:
        print(f"\n❌ Test suite runner failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    finally:
        # Restore original streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Combine stdout and stderr output
        combined_output = stdout_capture.getvalue()
        if stderr_capture.getvalue().strip():
            combined_output += "\n\n" + "="*40 + "\nSTDERR OUTPUT:\n" + "="*40 + "\n"
            combined_output += stderr_capture.getvalue()
        
        # Save the captured output
        test_type = "all_api" if include_api_tests else "all_mock"
        save_test_output(combined_output, test_type)
    
    return success

def run_specific_test(test_suite: str, test_number: int = None, include_api: bool = False):
    """Run a specific test suite or test number and capture output"""
    # Capture both stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    stdout_capture = TeeOutput(original_stdout)
    stderr_capture = TeeOutput(original_stderr)
    
    try:
        # Redirect output to capture
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        result = None
        
        if test_suite.lower() == "output":
            print("🧪 Running Output Parser Tests...")
            result = test_output_parser()
        
        elif test_suite.lower() == "ice" or test_suite.lower() == "icebreaker":
            print("🧪 Running Ice Breaker Tests...")
            result = run_linkedin_parser_tests(include_real_api=include_api)
        
        elif test_suite.lower() == "linkedin" or test_suite.lower() == "lookup":
            print("🧪 Running LinkedIn Lookup Agent Tests...")
            result = run_linkedin_lookup_tests(skip_api_tests=not include_api)
        
        elif test_suite.lower() == "conversation":
            print(f"🧪 Running Conversation Parser Tests{f' (Test {test_number})' if test_number else ''}...")
            result = run_conversation_tests(test_number)
        
        else:
            print("❌ Unknown test suite. Available options:")
            print("   'output' - Output Parser tests")
            print("   'ice' - Ice Breaker tests")
            print("   'linkedin' - LinkedIn Lookup Agent tests")
            print("   'conversation' - Conversation Parser tests")
            result = False
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        result = False
    
    finally:
        # Restore original streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Combine stdout and stderr output
        combined_output = stdout_capture.getvalue()
        if stderr_capture.getvalue().strip():
            combined_output += "\n\n" + "="*40 + "\nSTDERR OUTPUT:\n" + "="*40 + "\n"
            combined_output += stderr_capture.getvalue()
        
        # Save the captured output
        test_type = f"{test_suite}_{'api' if include_api else 'mock'}"
        save_test_output(combined_output, test_type, test_number)
    
    # Handle None results
    return result if result is not None else False

if __name__ == "__main__":
    # Parse command line arguments
    include_api = "--api" in sys.argv
    
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and "--api" in sys.argv):
        # No arguments (or just --api) - run all tests
        if include_api:
            print("Running all tests INCLUDING API calls...")
            print("⚠️ This will make real API requests and may consume credits!")
            print("⚠️ This will also generate REAL output files in the 'output/' folder!")
        else:
            print("Running all tests (mock/offline mode)...")
            print("Use --api flag to include real API tests and generate actual output files")
        
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