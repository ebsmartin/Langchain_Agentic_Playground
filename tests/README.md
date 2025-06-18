# Test Suite Documentation

This directory contains comprehensive tests for the Langchain Agentic Playground project. The test suite covers all major components including conversation parsing, LinkedIn profile lookup, ice breaker functionality, and output parsing.

## 📁 Test Structure

```
tests/
├── __init__.py                    # Package initialization
├── README.md                      # This documentation
├── run_all_tests.py              # Main test runner
├── test_conversation_parser.py   # Conversation analysis tests (6 input types)
├── test_linkedin_parser.py           # LinkedIn profile summarization tests
├── test_linkedin_lookup_agent.py # LinkedIn search and retrieval tests
└── test_output_parser.py         # Structured output parsing tests
```

## 🚀 Quick Start

### Run All Tests (Recommended)
```bash
# Run all tests in mock/offline mode (no API calls)
python tests/run_all_tests.py

# Run all tests including real API calls (⚠️ consumes API credits!)
python tests/run_all_tests.py --api
```

### Run Individual Test Suites
```bash
# Output Parser tests (no API calls needed)
python tests/run_all_tests.py output

# Ice Breaker tests (mock mode)
python tests/run_all_tests.py ice

# Ice Breaker tests with real API calls
python tests/run_all_tests.py ice --api

# LinkedIn Lookup Agent tests (basic validation)
python tests/run_all_tests.py linkedin

# LinkedIn Lookup Agent tests with real API calls
python tests/run_all_tests.py linkedin --api

# All Conversation Parser tests (6 different input types)
python tests/run_all_tests.py conversation

# Specific Conversation Parser test (e.g., audio test)
python tests/run_all_tests.py conversation 3
```

## 🧪 Individual Test Files

### 1. Conversation Parser Tests
Tests the core conversation analysis functionality with 6 different input types:

```bash
# Run all conversation tests
python tests/test_conversation_parser.py

# Run specific test by number
python tests/test_conversation_parser.py 1  # Direct text input
python tests/test_conversation_parser.py 2  # Text file (.txt)
python tests/test_conversation_parser.py 3  # Audio file (.mp3)
python tests/test_conversation_parser.py 4  # Image file (.png)
python tests/test_conversation_parser.py 5  # PDF file (.pdf)
python tests/test_conversation_parser.py 6  # Word document (.docx)
```

**Test Coverage:**
- ✅ Direct text conversation analysis
- ✅ Text file processing
- ✅ Audio transcription and analysis
- ✅ Image text extraction and analysis
- ✅ PDF content analysis
- ✅ Word document processing

### 2. Ice Breaker Tests
Tests LinkedIn profile summarization and ice breaker generation:

```bash
# Run all ice breaker tests (mock mode only)
python tests/test_linkedin_parser.py

# Include real API calls
python tests/test_linkedin_parser.py --real

# Test with specific person
python tests/test_linkedin_parser.py --real --name "John Doe"
```

**Test Coverage:**
- ✅ Mock mode functionality (no API calls)
- ✅ Output parser integration
- ✅ Pydantic model validation
- ✅ Real LinkedIn profile lookup (optional)
- ✅ Error handling and edge cases

### 3. LinkedIn Lookup Agent Tests
Tests the LinkedIn profile search and retrieval system:

```bash
# Run all LinkedIn agent tests (includes API calls by default)
python tests/test_linkedin_lookup_agent.py

# Skip API calls (validation only)
python tests/test_linkedin_lookup_agent.py --no-api
```

**Test Coverage:**
- ✅ API configuration validation
- ✅ Query parsing and formatting
- ✅ Different search query formats
- ✅ Error handling for edge cases
- ✅ Tool integration testing
- ✅ Real LinkedIn profile searches

### 4. Output Parser Tests
Tests structured LLM output parsing with Pydantic models:

```bash
# Run output parser tests
python tests/test_output_parser.py
```

**Test Coverage:**
- ✅ Structured output parsing
- ✅ Summary object creation
- ✅ Facts extraction
- ✅ Profile data retrieval

## 📋 Test Requirements

### Required Environment Variables
```bash
# Required for LinkedIn lookup and real API tests
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Required Python Packages
```bash
pip install python-docx  # For Word document processing
pip install langchain
pip install langchain-google-genai
pip install langchain-openai
pip install langchain-tavily
pip install pydantic
pip install python-dotenv
```

### Test Files Setup
For comprehensive testing, create these optional test files:

```bash
mkdir test_files

# Optional test files (tests will skip if not present):
test_files/conversation.mp3        # Audio conversation
test_files/business_card.png       # Image with text
test_files/conversation.pdf        # PDF with conversation text
```

Note: Text files (.txt) and Word documents (.docx) are created automatically by the tests.

## 🎯 Test Modes

### Mock Mode (Default)
- **No API calls** - Safe for development
- **No credits consumed** - Free to run repeatedly
- **Fast execution** - Perfect for rapid testing
- **Offline capable** - Works without internet

### API Mode (Optional)
- **Real API calls** - Tests actual functionality
- **Credits consumed** - Uses your API quotas
- **Slower execution** - Network dependent
- **Full validation** - End-to-end testing

## 📊 Understanding Test Results

### Success Indicators
```
✅ Test passed successfully
🎉 All tests passed!
🏆 ALL TESTS SUCCESSFUL!
```

### Warning Indicators
```
⚠️ Some tests failed - check output above
⚠️ Most tests passed - some issues detected
⏭️ Test skipped (missing files/API keys)
```

### Error Indicators
```
❌ Test failed with error
❌ Many tests failed - check configuration
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
ModuleNotFoundError: No module named 'conversation_parser'
```
**Solution:** Run tests from the project root directory or ensure Python path is correct.

**2. Missing API Keys**
```bash
❌ OPENAI_API_KEY: Missing or invalid
```
**Solution:** Add required API keys to your `.env` file.

**3. Missing Dependencies**
```bash
❌ Test 6 Failed: python-docx not installed
```
**Solution:** Install missing packages with `pip install python-docx`.

**4. File Not Found**
```bash
⏭️ Test 3 Skipped: No audio file found
```
**Solution:** Add test files to `test_files/` directory or ignore (tests will skip gracefully).

### Debug Mode
For detailed debugging, check individual test outputs:
```bash
# Each test prints detailed debug information
python tests/test_conversation_parser.py 3
```

## 🎨 Customization

### Running Tests with Custom Data

**Custom Ice Breaker Test:**
```bash
python tests/test_linkedin_parser.py --real --name "Your Target Person"
```

**Custom LinkedIn Search:**
```bash
# Edit test_linkedin_lookup_agent.py and modify the test_cases array
```

**Custom Conversation:**
```bash
# Edit test_conversation_parser.py and modify the conversation_text variable
```

### Adding New Tests

1. Create new test function in appropriate test file
2. Add to the respective `run_*_tests()` function
3. Update documentation

## 📈 Performance Expectations

### Mock Mode (Recommended for Development)
- **Duration:** ~30-60 seconds for all tests
- **API Calls:** 0
- **Credits Used:** 0

### API Mode (For Production Validation)
- **Duration:** ~3-5 minutes for all tests
- **API Calls:** ~15-25 requests
- **Credits Used:** Varies by provider

## 🎓 Best Practices

1. **Start with mock mode** during development
2. **Use API mode** before deployment
3. **Run specific tests** when debugging issues
4. **Check API quotas** before running API tests
5. **Keep test files small** for faster execution

## 📞 Support

If you encounter issues:

1. Check the console output for specific error messages
2. Verify your `.env` file has the required API keys
3. Ensure all dependencies are installed
4. Try running individual tests to isolate issues
5. Check the main project README for additional setup instructions

---

**Happy Testing! 🚀**