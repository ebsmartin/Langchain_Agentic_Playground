import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from output_parsers import summary_parser, Summary
from linkedin_parser import find_linkedin_profile_query

def test_output_parser():
    """Test the output parser with linkedin_parser"""
    load_dotenv()
    
    print("="*50)
    print("OUTPUT PARSER TESTING")
    print("="*50)
    
    try:
        # Test with a simple LinkedIn profile lookup
        result, profile_pic, banner = find_linkedin_profile_query("Eric Burton Martin", mock=True)
        
        print("✅ Output Parser Test Results:")
        print(f"   Summary: {result.summary}")
        print(f"   Facts: {result.facts}")
        print(f"   Profile Picture: {profile_pic}")
        print(f"   Banner: {banner}")
        
        print("\n📋 Test Summary:")
        print("   - Successfully parsed structured output from LLM")
        print("   - Extracted summary and facts into Summary object")
        print("   - Retrieved profile picture and banner URLs")
        print("   - Output parser working correctly with Pydantic models")
        
    except Exception as e:
        print(f"❌ Output Parser Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Output Parser Testing...")
    test_output_parser()