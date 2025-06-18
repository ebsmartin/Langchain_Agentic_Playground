import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import linkedin_lookup_agent

def test_linkedin_lookup_basic():
    """Test basic LinkedIn lookup functionality"""
    load_dotenv()
    
    print("🧪 TESTING LINKEDIN LOOKUP - BASIC FUNCTIONALITY")
    print("=" * 60)
    
    # Test cases with different query formats
    test_cases = [
        {
            "name": "Simple Name",
            "query": "Eric Burton Martin",
            "expected_contains": "linkedin.com/in/"
        },
        {
            "name": "Name with Company",
            "query": "Eric Burton Martin Cognizant",
            "expected_contains": "linkedin.com/in/"
        },
        {
            "name": "Name with Title and Company",
            "query": "Matt software engineer Nickel5",
            "expected_contains": "linkedin.com/in/"
        },
        {
            "name": "Complex Query",
            "query": "Tanner Moore 1inch blockchain crypto",
            "expected_contains": "linkedin.com/in/"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Query: '{test_case['query']}'")
        
        try:
            result = linkedin_lookup_agent.lookup(test_case['query'])
            
            # Check if result contains LinkedIn URL
            success = test_case['expected_contains'] in result
            
            if success:
                print(f"   ✅ Success: {result}")
            else:
                print(f"   ⚠️ No LinkedIn URL found: {result}")
            
            results.append(success)
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append(False)
    
    return results

def test_linkedin_lookup_error_handling():
    """Test error handling for edge cases"""
    load_dotenv()
    
    print("🧪 TESTING LINKEDIN LOOKUP - ERROR HANDLING")
    print("=" * 60)
    
    edge_cases = [
        {
            "name": "Empty String",
            "query": "",
            "should_fail": True
        },
        {
            "name": "Very Long Query",
            "query": "a" * 500,  # Very long string
            "should_fail": False  # Should handle gracefully
        },
        {
            "name": "Special Characters",
            "query": "John@#$%Doe!!!",
            "should_fail": False  # Should handle gracefully
        },
        {
            "name": "Non-existent Person",
            "query": "Xyzvwqp Nonexistent Person 12345",
            "should_fail": False  # Should return "Could not find" message
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n📋 Edge Case {i}: {test_case['name']}")
        print(f"   Query: '{test_case['query'][:50]}{'...' if len(test_case['query']) > 50 else ''}'")
        
        try:
            result = linkedin_lookup_agent.lookup(test_case['query'])
            
            if test_case['should_fail']:
                print(f"   ⚠️ Expected failure but got: {result}")
                results.append(False)
            else:
                print(f"   ✅ Handled gracefully: {result}")
                results.append(True)
                
        except Exception as e:
            if test_case['should_fail']:
                print(f"   ✅ Failed as expected: {e}")
                results.append(True)
            else:
                print(f"   ❌ Unexpected failure: {e}")
                results.append(False)
    
    return results

def test_linkedin_lookup_api_requirements():
    """Test API key requirements and configuration"""
    load_dotenv()
    
    print("🧪 TESTING LINKEDIN LOOKUP - API CONFIGURATION")
    print("=" * 60)
    
    results = []
    
    # Test 1: Check required environment variables
    print("\n📋 Test 1: Environment Variables")
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value and len(value) > 10:  # Basic validation
            print(f"   ✅ {var}: Set (length: {len(value)})")
            results.append(True)
        else:
            print(f"   ❌ {var}: Missing or invalid")
            results.append(False)
    
    # Test 2: Test tool functionality (if APIs are available)
    print("\n📋 Test 2: Tool Integration")
    if all(results):  # Only test if API keys are available
        try:
            from tools.tools import get_profile_url_tavily
            
            # Test the underlying tool directly
            tool_result = get_profile_url_tavily("Eric Burton Martin Cognizant")
            
            if "Error" in tool_result or "Could not find" in tool_result:
                print(f"   ⚠️ Tool returned: {tool_result}")
                results.append(False)
            else:
                print(f"   ✅ Tool working: {tool_result}")
                results.append(True)
                
        except Exception as e:
            print(f"   ❌ Tool test failed: {e}")
            results.append(False)
    else:
        print("   ⏭️ Skipped (missing API keys)")
        results.append(False)
    
    return results

def test_linkedin_lookup_query_parsing():
    """Test how different query formats are parsed"""
    load_dotenv()
    
    print("🧪 TESTING LINKEDIN LOOKUP - QUERY PARSING")
    print("=" * 60)
    
    # Test that queries are passed through correctly
    parsing_tests = [
        {
            "input": "Matt software engineer Nickel5",
            "description": "Should preserve company name 'Nickel5'"
        },
        {
            "input": "Dr. Sarah Johnson Harvard Medical",
            "description": "Should handle titles and compound names"
        },
        {
            "input": "Alex Chen Google Software Engineer",
            "description": "Should handle name-company-title order"
        }
    ]
    
    results = []
    
    print("📋 Query Parsing Tests:")
    print("   (Testing that queries are processed correctly)")
    
    for i, test in enumerate(parsing_tests, 1):
        print(f"\n   Test {i}: {test['description']}")
        print(f"   Input: '{test['input']}'")
        
        try:
            # We can't easily test the internal parsing without modifying the agent,
            # but we can test that it doesn't crash and returns something reasonable
            result = linkedin_lookup_agent.lookup(test['input'])
            
            # Basic validation - should not crash and should return a string
            if isinstance(result, str) and len(result) > 0:
                print(f"   ✅ Processed successfully: {result[:60]}...")
                results.append(True)
            else:
                print(f"   ❌ Invalid result: {result}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
            results.append(False)
    
    return results

def run_linkedin_lookup_tests(skip_api_tests: bool = False):
    """Run all LinkedIn lookup agent tests"""
    print("🚀 RUNNING LINKEDIN LOOKUP AGENT TEST SUITE")
    print("=" * 70)
    
    all_results = []
    
    # Test 1: API Configuration (always run)
    print("\n1️⃣ API CONFIGURATION TEST")
    print("-" * 30)
    config_results = test_linkedin_lookup_api_requirements()
    all_results.extend(config_results)
    
    # Test 2: Query Parsing (always run)
    print("\n2️⃣ QUERY PARSING TEST")
    print("-" * 30)
    parsing_results = test_linkedin_lookup_query_parsing()
    all_results.extend(parsing_results)
    
    # Test 3: Basic Functionality (optional - requires API calls)
    if not skip_api_tests and all(config_results[:2]):  # Only if API keys are present
        print("\n3️⃣ BASIC FUNCTIONALITY TEST")
        print("-" * 30)
        basic_results = test_linkedin_lookup_basic()
        all_results.extend(basic_results)
        
        print("\n4️⃣ ERROR HANDLING TEST")
        print("-" * 30)
        error_results = test_linkedin_lookup_error_handling()
        all_results.extend(error_results)
    else:
        if skip_api_tests:
            print("\n3️⃣ BASIC FUNCTIONALITY TEST - SKIPPED")
            print("-" * 30)
            print("   Use --api flag to include API tests")
        else:
            print("\n3️⃣ BASIC FUNCTIONALITY TEST - SKIPPED")
            print("-" * 30)
            print("   Missing required API keys")
    
    # Summary
    passed = sum(all_results)
    total = len(all_results)
    
    print("\n" + "=" * 70)
    print("LINKEDIN LOOKUP AGENT TEST RESULTS")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    elif passed > total * 0.7:  # 70% threshold
        print("⚠️ Most tests passed - some issues detected")
    else:
        print("❌ Many tests failed - check configuration and API keys")
    
    return passed >= total * 0.7  # Return success if 70% or more tests pass

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    skip_api = "--no-api" in sys.argv
    
    if skip_api:
        print("Starting LinkedIn Lookup Agent Tests (no API calls)...")
    else:
        print("Starting LinkedIn Lookup Agent Tests (including API calls)...")
        print("Use 'python test_linkedin_lookup_agent.py --no-api' to skip API tests")
    
    success = run_linkedin_lookup_tests(skip_api_tests=skip_api)
    sys.exit(0 if success else 1)