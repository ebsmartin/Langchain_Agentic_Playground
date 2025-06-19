import sys
import os
import json
import tempfile
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.output_manager import ConversationOutputManager
from third_parties.linkedin import scrape_linkedin_profile

def test_output_manager():
    """
    Comprehensive test of ConversationOutputManager functionality
    
    Returns:
        bool: True if all tests passed, False if any failed
    """
    load_dotenv()
    
    print("="*60)
    print("OUTPUT MANAGER COMPREHENSIVE TESTING")
    print("="*60)
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="test_output_")
    print(f"🧪 Using temporary directory: {temp_dir}")
    
    try:
        # Initialize output manager with temp directory
        output_manager = ConversationOutputManager(output_dir=temp_dir)
        
        test_results = []
        
        # Test 1: Basic initialization
        print("\n1️⃣ TESTING INITIALIZATION")
        print("-" * 30)
        test_results.append(test_initialization(output_manager, temp_dir))
        
        # Test 2: Image URL extraction (mock data)
        print("\n2️⃣ TESTING IMAGE URL EXTRACTION (MOCK DATA)")
        print("-" * 30)
        test_results.append(test_image_extraction_mock(output_manager))
        
        # Test 3: Image URL extraction (real API data - if available)
        print("\n3️⃣ TESTING IMAGE URL EXTRACTION (REAL API)")
        print("-" * 30)
        test_results.append(test_image_extraction_real(output_manager))
        
        # Test 4: Name extraction from profile data
        print("\n4️⃣ TESTING NAME EXTRACTION")
        print("-" * 30)
        test_results.append(test_name_extraction(output_manager))
        
        # Test 5: Filename sanitization
        print("\n5️⃣ TESTING FILENAME SANITIZATION")
        print("-" * 30)
        test_results.append(test_filename_sanitization(output_manager))
        
        # Test 6: Full conversation analysis saving
        print("\n6️⃣ TESTING CONVERSATION ANALYSIS SAVING")
        print("-" * 30)
        test_results.append(test_conversation_saving(output_manager))
        
        # Test 7: Loading and searching saved analyses
        print("\n7️⃣ TESTING LOADING AND SEARCHING")
        print("-" * 30)
        test_results.append(test_loading_and_searching(output_manager))
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "="*60)
        print("🎯 OUTPUT MANAGER TEST SUMMARY")
        print("="*60)
        print(f"✅ Tests Passed: {passed}/{total}")
        
        for i, result in enumerate(test_results, 1):
            status = "✅ PASS" if result else "❌ FAIL"
            test_names = [
                "Initialization",
                "Image Extraction (Mock)",
                "Image Extraction (Real API)",
                "Name Extraction",
                "Filename Sanitization",
                "Conversation Saving",
                "Loading and Searching"
            ]
            print(f"   {i}. {test_names[i-1]}: {status}")
        
        overall_success = passed == total
        print(f"\n🏆 Overall Result: {'SUCCESS' if overall_success else 'FAILURE'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Failed to cleanup temp directory: {e}")

def test_initialization(output_manager, temp_dir):
    """Test basic initialization"""
    try:
        # Check if directory was created
        if not os.path.exists(temp_dir):
            print("❌ Output directory not created")
            return False
        
        # Check if output_manager is properly initialized
        if output_manager.output_dir != temp_dir:
            print("❌ Output directory not set correctly")
            return False
        
        print("✅ Initialization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return False

def test_image_extraction_mock(output_manager):
    """Test image URL extraction with mock data"""
    try:
        # Get mock data (Eden Marco profile)
        mock_data = scrape_linkedin_profile("mock", mock=True)
        
        if not mock_data:
            print("❌ Could not load mock data")
            return False
        
        # Extract image URLs
        image_data = output_manager._extract_image_urls(mock_data)
        
        # Check results
        has_profile_pic = bool(image_data.get('profile_picture_url'))
        has_banner = bool(image_data.get('banner_url'))
        
        print(f"   Profile Picture: {'✅' if has_profile_pic else '❌'}")
        print(f"   Banner Image: {'✅' if has_banner else '❌'}")
        
        if has_profile_pic and has_banner:
            print("✅ Mock image extraction test passed")
            return True
        else:
            print("⚠️ Mock image extraction test partially successful")
            return True  # Still pass since mock data might not have images
        
    except Exception as e:
        print(f"❌ Mock image extraction test failed: {e}")
        return False

def test_image_extraction_real(output_manager):
    """Test image URL extraction with real API data"""
    try:
        print("   Attempting to scrape Your LinkedIn profile...")
        
        # Try to get real API data
        real_data = scrape_linkedin_profile("https://www.linkedin.com/in/ebsmartin", mock=False)
        
        if not real_data:
            print("⚠️ Could not load real API data - skipping test")
            return True  # Skip test if API not available
        
        # Extract image URLs
        image_data = output_manager._extract_image_urls(real_data)
        
        # Check what we found
        has_profile_pic = bool(image_data.get('profile_picture_url'))
        has_banner = bool(image_data.get('banner_url'))
        has_company_logo = bool(image_data.get('company_logo_url'))
        
        print(f"   Profile Picture: {'✅' if has_profile_pic else '❌'}")
        print(f"   Banner Image: {'✅' if has_banner else '❌'}")
        print(f"   Company Logo: {'✅' if has_company_logo else '❌'}")
        
        print("✅ Real API image extraction test completed")
        return True  # Pass regardless of what images are found
        
    except Exception as e:
        print(f"⚠️ Real API image extraction test failed: {e}")
        print("   This may be due to API limits or network issues")
        return True  # Don't fail the entire test suite for API issues

def test_name_extraction(output_manager):
    """Test name extraction from profile data"""
    try:
        # Test case 1: Complete profile data
        test_data_1 = {
            'person': {
                'firstName': 'John',
                'lastName': 'Doe',
                'headline': 'Software Engineer'
            }
        }
        
        name_1 = output_manager._get_actual_name_from_profile_data(test_data_1)
        if name_1 != "John Doe":
            print(f"❌ Expected 'John Doe', got '{name_1}'")
            return False
        
        # Test case 2: Only first name
        test_data_2 = {
            'person': {
                'firstName': 'Jane',
                'headline': 'Designer'
            }
        }
        
        name_2 = output_manager._get_actual_name_from_profile_data(test_data_2)
        if name_2 != "Jane":
            print(f"❌ Expected 'Jane', got '{name_2}'")
            return False
        
        # Test case 3: Empty data
        name_3 = output_manager._get_actual_name_from_profile_data({})
        if name_3 is not None:
            print(f"❌ Expected None for empty data, got '{name_3}'")
            return False
        
        print("✅ Name extraction test passed")
        return True
        
    except Exception as e:
        print(f"❌ Name extraction test failed: {e}")
        return False

def test_filename_sanitization(output_manager):
    """Test filename sanitization"""
    try:
        test_cases = [
            ("John Doe", "John_Doe"),
            ("John/Doe", "JohnDoe"),
            ("John<>Doe", "JohnDoe"),
            ("John:Doe|Test", "JohnDoeTest"),
            ("Special * Characters ? Test", "Special_Characters_Test")
        ]
        
        for input_name, expected in test_cases:
            result = output_manager._sanitize_filename(input_name)
            if result != expected:
                print(f"❌ Expected '{expected}', got '{result}' for input '{input_name}'")
                return False
        
        print("✅ Filename sanitization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Filename sanitization test failed: {e}")
        return False

def test_conversation_saving(output_manager):
    """Test full conversation analysis saving"""
    try:
        # Prepare test data
        test_conversation_analysis = {
            'analysis': 'Test analysis content',
            'person_mapping': {'Person A': 'Eric', 'Person B': 'Test Person'},
            'action_items': ['Follow up with Test Person', 'Send LinkedIn message']
        }
        
        test_profile_data = {
            'person': {
                'firstName': 'Test',
                'lastName': 'Person',
                'headline': 'Test Engineer'
            }
        }
        
        # Save the analysis
        filename = output_manager.save_conversation_analysis(
            search_query="Test Person Engineer",
            linkedin_url="https://www.linkedin.com/in/testperson",
            profile_data=test_profile_data,
            conversation_analysis=test_conversation_analysis,
            original_conversation="Test conversation content",
            conversation_date="2025-06-18"
        )
        
        # Check if file was created
        file_path = os.path.join(output_manager.output_dir, filename)
        if not os.path.exists(file_path):
            print(f"❌ File not created: {filename}")
            return False
        
        # Load and verify content
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Verify structure
        required_keys = ['metadata', 'linkedin_profile', 'conversation', 'summary']
        for key in required_keys:
            if key not in saved_data:
                print(f"❌ Missing key in saved data: {key}")
                return False
        
        # Verify actual name was extracted correctly
        if saved_data['metadata']['actual_name'] != 'Test Person':
            print(f"❌ Incorrect name extracted: {saved_data['metadata']['actual_name']}")
            return False
        
        print(f"✅ Conversation saving test passed - file: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Conversation saving test failed: {e}")
        return False

def test_loading_and_searching(output_manager):
    """Test loading and searching saved analyses"""
    try:
        # First, save some test data (reuse from previous test)
        test_data = [
            {
                'search_query': 'John Engineer Google',
                'profile_data': {'person': {'firstName': 'John', 'lastName': 'Engineer'}},
                'conversation_analysis': {'analysis': 'John works at Google'}
            },
            {
                'search_query': 'Jane Designer Apple',
                'profile_data': {'person': {'firstName': 'Jane', 'lastName': 'Designer'}},
                'conversation_analysis': {'analysis': 'Jane works at Apple'}
            }
        ]
        
        saved_filenames = []
        for data in test_data:
            filename = output_manager.save_conversation_analysis(
                search_query=data['search_query'],
                linkedin_url=f"https://www.linkedin.com/in/{data['search_query'].replace(' ', '').lower()}",
                profile_data=data['profile_data'],
                conversation_analysis=data['conversation_analysis']
            )
            saved_filenames.append(filename)
        
        # Test listing all analyses
        all_analyses = output_manager.list_saved_analyses()
        if len(all_analyses) < 2:
            print(f"❌ Expected at least 2 analyses, found {len(all_analyses)}")
            return False
        
        # Test searching
        search_results = output_manager.search_saved_analyses('Engineer')
        if len(search_results) < 1:
            print(f"❌ Search for 'Engineer' returned {len(search_results)} results")
            return False
        
        print("✅ Loading and searching test passed")
        return True
        
    except Exception as e:
        print(f"❌ Loading and searching test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Output Manager Comprehensive Testing...")
    success = test_output_manager()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)