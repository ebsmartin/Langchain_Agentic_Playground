import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_parser import find_linkedin_profile_query
from output_parsers import Summary

def test_linkedin_parser_mock():
    """Test linkedin_parser with mock data (no API calls)"""
    load_dotenv()
    
    print("🧪 TESTING ICE BREAKER - MOCK MODE")
    print("=" * 50)
    
    try:
        # Test with mock=True to avoid API calls
        result, profile_pic, banner = find_linkedin_profile_query("Eric Burton Martin", mock=True)
        
        # Validate the result is a Summary object
        assert isinstance(result, Summary), f"Expected Summary object, got {type(result)}"
        
        # Validate Summary fields
        assert hasattr(result, 'summary'), "Summary object missing 'summary' field"
        assert hasattr(result, 'facts'), "Summary object missing 'facts' field"
        assert isinstance(result.summary, str), "Summary should be a string"
        assert isinstance(result.facts, list), "Facts should be a list"
        
        print("✅ Mock Test Results:")
        print(f"   Summary type: {type(result)}")
        print(f"   Summary length: {len(result.summary)} characters")
        print(f"   Facts count: {len(result.facts)}")
        print(f"   Profile picture: {profile_pic}")
        print(f"   Banner: {banner}")
        
        # Show sample content
        print(f"\n📋 Sample Content:")
        print(f"   Summary preview: {result.summary[:100]}...")
        if result.facts:
            print(f"   First fact: {result.facts[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_linkedin_parser_real(test_name: str = "Eric Burton Martin"):
    """Test linkedin_parser with real API calls (optional)"""
    load_dotenv()
    
    print(f"🧪 TESTING ICE BREAKER - REAL MODE ({test_name})")
    print("=" * 50)
    
    try:
        # Test with real API calls
        result, profile_pic, banner = find_linkedin_profile_query(test_name, mock=False)
        
        # Validate the result
        assert isinstance(result, Summary), f"Expected Summary object, got {type(result)}"
        
        print("✅ Real API Test Results:")
        print(f"   Summary type: {type(result)}")
        print(f"   Summary length: {len(result.summary)} characters")
        print(f"   Facts count: {len(result.facts)}")
        print(f"   Profile picture: {profile_pic}")
        print(f"   Banner: {banner}")
        
        # Show actual content
        print(f"\n📋 Actual Content:")
        print(f"   Summary: {result.summary}")
        print(f"   Facts: {result.facts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real API Test Failed: {e}")
        print("   This might be due to API keys, rate limits, or network issues")
        import traceback
        traceback.print_exc()
        return False

def test_linkedin_parser_output_parser():
    """Test the output parser integration specifically"""
    load_dotenv()
    
    print("🧪 TESTING ICE BREAKER - OUTPUT PARSER INTEGRATION")
    print("=" * 50)
    
    try:
        # Test with mock data
        result, _, _ = find_linkedin_profile_query("Test User", mock=True)
        
        # Test Summary object methods
        summary_dict = result.to_dict()
        
        assert isinstance(summary_dict, dict), "to_dict() should return a dictionary"
        assert 'summary' in summary_dict, "Dictionary should contain 'summary' key"
        assert 'facts' in summary_dict, "Dictionary should contain 'facts' key"
        
        print("✅ Output Parser Integration Test Results:")
        print(f"   to_dict() works: {isinstance(summary_dict, dict)}")
        print(f"   Dictionary keys: {list(summary_dict.keys())}")
        print(f"   Dictionary structure valid: {'summary' in summary_dict and 'facts' in summary_dict}")
        
        # Test Pydantic validation
        try:
            # Try to create a new Summary object with the same data
            new_summary = Summary(summary=result.summary, facts=result.facts)
            print(f"   Pydantic validation works: {isinstance(new_summary, Summary)}")
        except Exception as validation_error:
            print(f"   Pydantic validation failed: {validation_error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Output Parser Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_linkedin_parser_tests(include_real_api: bool = False, test_name: str = "Eric Burton Martin"):
    """Run all linkedin_parser tests"""
    print("🚀 RUNNING ICE BREAKER TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Mock mode (always run)
    print("\n1️⃣ MOCK MODE TEST")
    print("-" * 30)
    results.append(test_linkedin_parser_mock())
    
    # Test 2: Output parser integration (always run)
    print("\n2️⃣ OUTPUT PARSER INTEGRATION TEST")
    print("-" * 30)
    results.append(test_linkedin_parser_output_parser())
    
    # Test 3: Real API mode (optional)
    if include_real_api:
        print("\n3️⃣ REAL API TEST")
        print("-" * 30)
        results.append(test_linkedin_parser_real(test_name))
    else:
        print("\n3️⃣ REAL API TEST - SKIPPED")
        print("-" * 30)
        print("   Use --real flag to include real API tests")
        print("   Example: python test_linkedin_parser.py --real")
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print("ICE BREAKER TEST RESULTS")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed - check output above")
    
    return passed == total

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    include_real = "--real" in sys.argv
    test_name = "Eric Burton Martin"  # Default test name
    
    # Check if a custom name was provided
    for i, arg in enumerate(sys.argv):
        if arg == "--name" and i + 1 < len(sys.argv):
            test_name = sys.argv[i + 1]
    
    if include_real:
        print(f"Starting Ice Breaker Tests (including real API calls for '{test_name}')...")
    else:
        print("Starting Ice Breaker Tests (mock mode only)...")
        print("Use 'python test_linkedin_parser.py --real' to include real API tests")
        print("Use 'python test_linkedin_parser.py --real --name \"John Doe\"' to test with a specific name")
    
    success = run_linkedin_parser_tests(include_real, test_name)
    sys.exit(0 if success else 1)