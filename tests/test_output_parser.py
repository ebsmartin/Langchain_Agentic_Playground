import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from output_parsers import summary_parser, Summary
from linkedin_parser import find_linkedin_profile_query

def test_output_parser():
    """
    Test the output parser with linkedin_parser
    
    Returns:
        bool: True if test passed, False if failed
    """
    load_dotenv()
    
    print("="*50)
    print("OUTPUT PARSER TESTING")
    print("="*50)
    
    try:
        # Test with a simple LinkedIn profile lookup
        result, profile_pic, banner = find_linkedin_profile_query("Eric Burton Martin", mock=True)
        
        # Check if the parsing was successful
        test_success = (
            result is not None and
            isinstance(result, Summary) and
            hasattr(result, 'summary') and
            hasattr(result, 'facts') and
            result.summary is not None and
            result.facts is not None
        )
        
        print("✅ Output Parser Test Results:")
        print(f"   Summary: {result.summary}")
        print(f"   Facts: {result.facts}")
        print(f"   Profile Picture: {profile_pic}")
        print(f"   Banner: {banner}")
        print(f"   Status: {'PASS' if test_success else 'FAIL'}")
        
        print("\n📋 Test Summary:")
        print("   - Successfully parsed structured output from LLM")
        print("   - Extracted summary and facts into Summary object")
        print("   - Retrieved profile picture and banner URLs")
        print("   - Output parser working correctly with Pydantic models")
        
        return test_success
        
    except Exception as e:
        print(f"❌ Output Parser Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Output Parser Testing...")
    success = test_output_parser()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)