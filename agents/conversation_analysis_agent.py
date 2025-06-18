import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import google.generativeai as genai
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from tools.tools import process_file_for_gemini, extract_text_from_word


def analyze_input_for_linkedin(input_data: str, is_file_path: bool = False, user_identity: dict = None) -> dict:
    """
    Analyzes various input types using Gemini's native multimodal capabilities.
    Excludes the user from LinkedIn search queries.
    """
    load_dotenv()
    
    if is_file_path:
        file_data = process_file_for_gemini(input_data)
        
        if file_data['send_to_gemini']:
            # Send directly to Gemini (audio, PDF, images)
            return analyze_with_gemini_native(file_data, user_identity)
        elif file_data['type'] == 'word':
            # Use agent only for Word docs
            return analyze_with_agent_for_word(input_data, user_identity)
        else:
            # Text content extracted - analyze directly
            return analyze_text_directly(file_data['content'], user_identity)
    else:
        # Direct text analysis
        return analyze_text_directly(input_data, user_identity)

def analyze_with_gemini_native(file_data: dict, user_identity: dict = None) -> dict:
    """
    Uses Gemini's native multimodal processing for audio, PDF, and images.
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    user_exclusion_text = ""
    if user_identity:
        user_name = user_identity.get('name', '')
        user_title = user_identity.get('title', '')
        user_company = user_identity.get('company', '')
        user_exclusion_text = f"""
        IMPORTANT: EXCLUDE the following person from your analysis (this is the user themselves):
        - Name: {user_name}
        - Title: {user_title}
        - Company: {user_company}
        
        Do NOT create LinkedIn search queries for {user_name}. Only analyze OTHER people in the content.
        """
    
    # Enhanced prompt for audio files
    if file_data['type'] == 'audio':
        prompt = f"""
        AUDIO TRANSCRIPTION AND ANALYSIS:
        
        First, carefully transcribe this audio file. Pay special attention to:
        - Names (which might sound like other words - e.g., "Ten or More" could be "Tanner Moore")
        - Job titles and company names
        - Professional conversations and introductions
        
        Then analyze the transcribed content for personal information that can be used to create LinkedIn search queries.
        
        {user_exclusion_text}
        
        Look for:
        1. Names of people mentioned (EXCLUDING the user mentioned above) - Be careful with similar-sounding words
        2. Job titles, roles, companies, or work locations mentioned
        3. Any relevant context that indicates a person's profession or industry
        4. Any contact information or professional details
        5. Any school or educational information
        6. Any social media handles or professional networks mentioned
        
        For each person identified (EXCLUDING the user), create a LinkedIn search query that uses any information in steps 1-6 above.
        
        IMPORTANT: If you hear words that sound like they could be names (e.g., "Ten or More" → "Tanner Moore"), 
        consider both possibilities and use context clues to determine the most likely interpretation.
        
        Format your response:
        
        TRANSCRIPTION:
        [Full transcription of the audio]
        
        ANALYSIS:
        For example, if you found "FirstName LastName JobTitle" for Person1:
        PERSON 1: [FirstName] - [LastName] - [JobTitle] - SEARCH: "[Search Query]"
        
        If no clear person information is found (other than the excluded user), respond with: "NO PERSONS IDENTIFIED"
        """
    else:
        prompt = f"""
        Analyze this content for personal information that can be used to create LinkedIn search queries.
        This can include names, job titles, companies, or any relevant details that can help identify people.
        
        {user_exclusion_text}
        
        Look for:
        1. Names of people mentioned (EXCLUDING the user mentioned above)
        2. Job titles, roles, companies, or work locations mentioned
        3. Any relevant context that indicates a person's profession or industry
        4. Any contact information or professional details
        5. Any school or educational information
        6. Any social media handles or professional networks mentioned
        
        For each person identified (EXCLUDING the user), create a LinkedIn search query that uses any information in steps 1-6 above.
        For example:
        "FirstName LastName JobTitle" or "FirstName LastName Company" or "FirstName Company School Name", etc.
        
        Format your response based on the information found above:
        For example, if you found "FirstName LastName JobTitle" for Person1 and "FirstName Company School" for Person 2:

        PERSON 1: [FirstName] - [LastName] - [JobTitle] - SEARCH: "[Search Query]"
        PERSON 2: [FirstName] - [Company] - [School] - SEARCH: "[Search Query]"
        
        If no clear person information is found (other than the excluded user), respond with: "NO PERSONS IDENTIFIED"
        """
    
    try:
        # Upload file and analyze with Gemini
        myfile = genai.upload_file(file_data['file_path'])
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([prompt, myfile])
        
        search_queries = parse_output_for_queries(response.text)
        
        return {
            'raw_output': response.text,
            'search_queries': search_queries
        }
        
    except Exception as e:
        return {
            'raw_output': f"Error processing {file_data['type']}: {str(e)}",
            'search_queries': []
        }

def analyze_text_directly(text: str, user_identity: dict = None) -> dict:
    """
    Analyzes text directly with Gemini.
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    user_exclusion_text = ""
    if user_identity:
        user_name = user_identity.get('name', '')
        user_title = user_identity.get('title', '')
        user_company = user_identity.get('company', '')
        user_school = user_identity.get('school', '')
        
        # Create comprehensive user exclusion with variations
        name_variations = [user_name]
        if ' ' in user_name:
            # Add first name only
            first_name = user_name.split()[0]
            name_variations.append(first_name)
            # Add last name only
            last_name = user_name.split()[-1]
            name_variations.append(last_name)
        
        user_exclusion_text = f"""
        CRITICAL: EXCLUDE the following person from your analysis (this is the USER themselves):
        - Full Name: {user_name}
        - Common Name Variations: {', '.join(name_variations)}
        - Title: {user_title}
        - Company: {user_company}
        - School: {user_school}
        
        DO NOT create LinkedIn search queries for ANY variation of {user_name} or {', '.join(name_variations)}.
        
        If you see "{first_name if ' ' in user_name else user_name}" mentioned in the conversation, this is the USER.
        If you see someone from "{user_company}" who does "{user_title}" work, this might be the USER.
        
        ONLY analyze OTHER people in the content, NOT the user.
        """
    
    prompt = f"""
    Analyze this text/conversation for personal information that can be used to create LinkedIn search queries: {text}
    
    {user_exclusion_text}
    
    STEP 1: First, identify who is the user in this conversation based on the exclusion criteria above.
    STEP 2: Then, look for OTHER people (not the user) and extract:
    1. Names of people mentioned (EXCLUDING the user mentioned above)
    2. Job titles, roles, companies, or work locations mentioned
    3. Any relevant context that indicates a person's profession or industry
    4. Any contact information or professional details
    5. Any school or educational information
    6. Any social media handles or professional networks mentioned
    
    For each person identified (EXCLUDING the user), create a LinkedIn search query that uses any information in steps 1-6 above.
    For example:
    "FirstName LastName JobTitle" or "FirstName LastName Company" or "FirstName Company School Name", etc.
    
    Format your response based on the information found above:
    For example, if you found "FirstName LastName JobTitle" for Person1 and "FirstName Company School" for Person 2:

    USER IDENTIFIED: [Name of the user who should be excluded]

    PERSON 1: [FirstName] - [LastName] - [JobTitle] - SEARCH: "[Search Query]"
    PERSON 2: [FirstName] - [Company] - [School] - SEARCH: "[Search Query]"
    
    If no clear person information is found (other than the excluded user), respond with: "NO PERSONS IDENTIFIED"
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        search_queries = parse_output_for_queries(response.text)
        
        return {
            'raw_output': response.text,
            'search_queries': search_queries
        }
    except Exception as e:
        return {
            'raw_output': f"Error: {str(e)}",
            'search_queries': []
        }

def analyze_with_agent_for_word(file_path: str, user_identity: dict = None) -> dict:
    """
    Only used for Word documents that need text extraction.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )
    
    user_exclusion_text = ""
    if user_identity:
        user_name = user_identity.get('name', '')
        user_title = user_identity.get('title', '')
        user_company = user_identity.get('company', '')
        user_exclusion_text = f"""
        IMPORTANT: EXCLUDE the following person from your analysis (this is the user themselves):
        - Name: {user_name}
        - Title: {user_title}
        - Company: {user_company}
        
        Do NOT create LinkedIn search queries for {user_name}. Only analyze OTHER people in the content.
        """
    
    tools_for_agent = [
        Tool(
            name="Extract Word Text",
            func=extract_text_from_word,
            description="Extracts text content from Word documents (.docx, .doc).",
        )
    ]

    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, prompt=react_prompt, tools=tools_for_agent)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    input_prompt = f"""
    Extract text from the Word document at: {file_path}
    Then analyze the text for personal information that can be used to create LinkedIn search queries.
    
    {user_exclusion_text}
    
    Look for:
    1. Names of people mentioned (EXCLUDING the user mentioned above)
    2. Job titles, roles, companies, or work locations mentioned
    3. Any relevant context that indicates a person's profession or industry
    4. Any contact information or professional details
    5. Any school or educational information
    6. Any social media handles or professional networks mentioned
    
    For each person identified (EXCLUDING the user), create a LinkedIn search query that uses any information in steps 1-6 above.
    
    Format your final answer based on the information found:
    For example, if you found "FirstName LastName JobTitle" for Person1 and "FirstName Company School" for Person 2:

    PERSON 1: [FirstName] - [LastName] - [JobTitle] - SEARCH: "[Search Query]"
    PERSON 2: [FirstName] - [Company] - [School] - SEARCH: "[Search Query]"
    
    If no clear person information is found (other than the excluded user), respond with: "NO PERSONS IDENTIFIED"
    """

    result = agent_executor.invoke(input={"input": input_prompt})
    search_queries = parse_output_for_queries(result["output"])
    
    return {
        'raw_output': result["output"],
        'search_queries': search_queries
    }

def parse_output_for_queries(output: str) -> list[str]:
    """
    Parses output to extract LinkedIn search queries with better company name extraction.
    """
    queries = []
    lines = output.split('\n')
    
    # Method 1: Look for SEARCH: "[query]" format (most reliable)
    for line in lines:
        if 'SEARCH:' in line and '"' in line:
            start = line.find('"')
            end = line.rfind('"')
            if start != -1 and end != -1 and start != end:
                query = line[start+1:end].strip()
                if query and len(query) > 2:
                    queries.append(query)
    
    # Method 2: If no SEARCH: format found, look for PERSON entries and build better queries
    if not queries:
        for line in lines:
            if line.strip().startswith('PERSON') and ':' in line:
                # Parse "PERSON 1: [FirstName] - [LastName] - [JobTitle] - [Company] - SEARCH: ..."
                parts = line.split(':', 1)
                if len(parts) > 1:
                    # Split by dashes and clean up
                    info_parts = [part.strip() for part in parts[1].split('-')]
                    # Remove bracketed placeholders and empty parts
                    useful_parts = []
                    for part in info_parts:
                        part = part.strip()
                        if part and not part.startswith('[') and not part.startswith('SEARCH'):
                            # Clean up any quotes or extra formatting
                            part = part.replace('"', '').replace("'", "")
                            useful_parts.append(part)
                    
                    if useful_parts:
                        # Create a more comprehensive query
                        if len(useful_parts) >= 3:
                            # Name + Title + Company format
                            query = f"{useful_parts[0]} {useful_parts[1]} {useful_parts[2]}"
                        elif len(useful_parts) == 2:
                            # Name + Company/Title format  
                            query = f"{useful_parts[0]} {useful_parts[1]}"
                        else:
                            query = useful_parts[0]
                        
                        if len(query) > 2:
                            queries.append(query)
    
    # Method 3: Enhanced text parsing for missed cases
    if not queries:
        # Look for patterns like "I'm [Name], [title] at [Company]"
        import re
        
        patterns = [
            r"I'm\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*),\s*([^.]+?)\s+at\s+([A-Z][a-zA-Z0-9]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*),\s*([^.]+?)\s+at\s+([A-Z][a-zA-Z0-9]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)\s+(?:is|works as)?\s*([^.]+?)\s+at\s+([A-Z][a-zA-Z0-9]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for match in matches:
                name, title, company = match
                # Clean up the title (remove extra words)
                title = title.replace('software engineer', 'Software Engineer').strip()
                query = f"{name.strip()} {title.strip()} {company.strip()}"
                if len(query) > 5:
                    queries.append(query)
    
    return list(set(queries))  # Remove duplicates

if __name__ == "__main__":
    # Test with user identity
    user_identity = {
        'name': 'Eric Burton Martin',
        'title': 'Healthcare Data Analyst',
        'company': 'Cognizant'
    }
    
    conversation = """
    Person A: I'm Eric Burton Martin, Healthcare Data Analyst at Cognizant.
    Person B: Nice to meet you! I'm Alex Johnson, smart contract developer at BlockchainSolutions.
    """
    
    print("Testing conversation analysis with user exclusion...")
    result = analyze_input_for_linkedin(conversation, is_file_path=False, user_identity=user_identity)
    
    print("Raw Output:")
    print(result['raw_output'])
    print("\nExtracted Search Queries (Should exclude Eric Burton Martin):")
    for query in result['search_queries']:
        print(f"- {query}")