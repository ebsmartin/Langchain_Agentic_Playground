"""
Test suite for the Langchain Agentic Playground

This package contains comprehensive tests for:
- Conversation Parser (6 different input types)
- Output Parser (structured LLM output parsing)
- Ice Breaker (LinkedIn profile summarization)
- LinkedIn Lookup Agent (profile search and retrieval)
- LinkedIn Integration (end-to-end workflow)
- File Processing Tools

Run tests with:
    python -m tests.run_all_tests
    python tests/run_all_tests.py
    python tests/run_all_tests.py --api                    # Include real API calls
    python tests/test_conversation_parser.py 3
    python tests/test_linkedin_parser.py --real
    python tests/test_linkedin_lookup_agent.py --no-api
    python tests/test_output_parser.py
"""

# Make test functions available at package level
from .test_conversation_parser import run_conversation_tests
from .test_output_parser import test_output_parser
from .test_linkedin_parser import run_linkedin_parser_tests
from .test_linkedin_lookup_agent import run_linkedin_lookup_tests

__all__ = [
    'run_conversation_tests', 
    'test_output_parser',
    'run_linkedin_parser_tests',
    'run_linkedin_lookup_tests'
]