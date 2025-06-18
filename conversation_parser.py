from langchain_core.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from agents import linkedin_lookup_agent
from agents.conversation_analysis_agent import analyze_input_for_linkedin
from linkedin_parser import find_linkedin_profile_query
from datetime import datetime, timedelta

def analyze_conversation_and_find_linkedin_profiles(
    input_data: str, 
    user_identity: dict = None, 
    is_file_path: bool = False,
    conversation_date: str = None
):
    """
    Analyzes a conversation and attempts to find LinkedIn profiles for people mentioned,
    excluding the user themselves.
    """
    load_dotenv()
    
    if conversation_date is None:
        conversation_date = datetime.now().strftime('%Y-%m-%d')
    
    print("=== STEP 1: ANALYZING CONVERSATION ===")
    
    if is_file_path:
        # Use the conversation analysis agent for file processing
        analysis_result = analyze_input_for_linkedin(input_data, is_file_path=True, user_identity=user_identity)
        
        # Extract conversation content for detailed analysis
        conversation_content = None
        
        if input_data.endswith('.txt'):
            # Read text files directly
            with open(input_data, 'r', encoding='utf-8') as f:
                conversation_content = f.read()
        else:
            # For audio, PDF, images - extract content from analysis result
            raw_output = analysis_result.get('raw_output', '')
            
            # Try to extract meaningful conversation content
            if raw_output:
                # Look for conversation patterns in the output
                lines = raw_output.split('\n')
                content_lines = []
                
                # Extract lines that look like conversation content
                for line in lines:
                    line = line.strip()
                    if (line.startswith('Person A:') or 
                        line.startswith('Person B:') or 
                        'TRANSCRIPTION:' in line or
                        ('I' in line and ('met' in line or 'spoke' in line))):
                        content_lines.append(line)
                
                if content_lines:
                    conversation_content = '\n'.join(content_lines)
                else:
                    # Use the full raw output as conversation content
                    conversation_content = raw_output
            
            # If still no content, create a summary from the search queries
            if not conversation_content and analysis_result.get('search_queries'):
                queries = analysis_result['search_queries']
                conversation_content = f"Audio/file content mentioned the following people: {', '.join(queries)}"
        
        # Use your existing detailed analysis function with ChatGoogleGenerativeAI
        detailed_analysis = get_detailed_conversation_analysis(
            conversation=conversation_content,
            user_identity=user_identity,
            conversation_date=conversation_date,
            is_file_path=False
        )
    else:
        # Direct conversation analysis - both use same input
        analysis_result = analyze_input_for_linkedin(input_data, is_file_path=False, user_identity=user_identity)
        
        detailed_analysis = get_detailed_conversation_analysis(
            conversation=input_data,
            user_identity=user_identity,
            conversation_date=conversation_date
        )
    
    print("=== DETAILED CONVERSATION ANALYSIS ===")
    print(detailed_analysis['analysis'])
    
    print("\n=== LINKEDIN SEARCH QUERIES (Excluding User) ===")
    filtered_queries = analysis_result['search_queries']
    for query in filtered_queries:
        print(f"- {query}")
    
    # Step 2: LinkedIn lookup
    print("\n=== STEP 2: LINKEDIN LOOKUP ===")
    
    linkedin_profiles = []
    for query in filtered_queries:
        print(f"\n🔍 Searching for: {query}")
        try:
            linkedin_url = linkedin_lookup_agent.lookup(query)
            linkedin_profiles.append({
                'search_query': query,
                'linkedin_url': linkedin_url
            })
            print(f"✅ Found: {linkedin_url}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            linkedin_profiles.append({
                'search_query': query,
                'linkedin_url': None,
                'error': str(e)
            })
    
    return {
        'detailed_analysis': detailed_analysis,
        'search_queries': filtered_queries,
        'linkedin_profiles': linkedin_profiles,
        'user_excluded': user_identity['name'] if user_identity else None
    }

def get_detailed_conversation_analysis(
    conversation: str = None, 
    user_identity: dict = None, 
    conversation_date: str = None,
    is_file_path: bool = False,
    file_path: str = None
):
    """
    Provides detailed conversation analysis with person mapping and personalized action items.
    """
    user_name = user_identity['name'] if user_identity else "the user"
    user_title = user_identity.get('title', '')
    user_company = user_identity.get('company', '')
    
    tomorrow_date = (datetime.strptime(conversation_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # DEBUG: Print what content we're actually analyzing
    if is_file_path:
        print(f"🐛 DEBUG: Analyzing file: {file_path}")
        if file_path and file_path.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    actual_content = f.read()
                print(f"🐛 DEBUG: File content: '{actual_content[:200]}...'")
                conversation = actual_content  # Use the actual file content
            except Exception as e:
                print(f"🐛 DEBUG: Error reading file: {e}")
                conversation = "ERROR: Could not read file content"
        else:
            print(f"🐛 DEBUG: Non-text file, using provided conversation: '{str(conversation)[:200]}...'")
    else:
        print(f"🐛 DEBUG: Analyzing direct text: '{str(conversation)[:200]}...'")
    
    if not conversation:
        return {
            'analysis': 'ERROR: No conversation content to analyze',
            'person_mapping': {},
            'action_items': []
        }
    
    # Enhanced template for detailed analysis
    summary_template = f"""
    Analyze the following conversation with strict attention to accuracy:
    
    CONVERSATION CONTENT:
    {conversation}
    
    CONTEXT:
    - User Identity: {user_name} ({user_title} at {user_company})
    - Conversation Date: {conversation_date}
    - Tomorrow's Date: {tomorrow_date}
    
    CRITICAL INSTRUCTION: Only analyze the content provided above. Do NOT invent, fabricate, or add any information not explicitly present in the conversation.
    
    Please do the following:
    
    1. **Person Mapping**: Map each Person A, Person B, etc. to their actual names ONLY if mentioned in the conversation.
    
    2. **People Identification** (EXCLUDE {user_name}):
    For each person OTHER THAN {user_name}, identify ONLY information explicitly stated in the conversation:
    - Name (only if explicitly mentioned)
    - Job title/role/company (only if explicitly mentioned)
    - Any other details (only if explicitly mentioned)
    
    3. **Conversation Summary**: Summarize only what actually happened in the conversation.
    
    4. **Key Points Discussed**: List only topics actually discussed in the provided conversation.
    
    5. **Action Items**: Create action items based only on commitments or plans mentioned in the conversation.
    
    IMPORTANT: If information is not explicitly stated in the conversation, do not include it. Do not make assumptions or add details.
    
    Format your response like this:
    
    ## Person Mapping:
    - Person A: [Name if mentioned, otherwise "Not specified"]
    - Person B: [Name if mentioned, otherwise "Not specified"]
    
    ## People Identified (Excluding {user_name}):
    **[Person Name if known]:**
    - Job Title/Role: [Only if explicitly mentioned]
    - Company/Industry: [Only if explicitly mentioned]
    - Other Details: [Only if explicitly mentioned]
    
    ## Conversation Summary:
    [Summary based only on the provided conversation content]
    
    ## Key Points Discussed:
    - [Only points actually discussed in the conversation]
    
    ## Action Items for {user_name}:
    - [Only actions/commitments mentioned in the conversation]
    """

    summary_prompt_template = PromptTemplate(
        input_variables=[], template=summary_template
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,  # Use 0 temperature for more consistent results
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    chain = summary_prompt_template | llm
    result = chain.invoke(input={})
    
    return {
        'analysis': result.content,
        'person_mapping': extract_person_mapping(result.content),
        'action_items': extract_action_items(result.content)
    }

def extract_person_mapping(analysis_text: str) -> dict:
    """
    Extracts person mapping from analysis.
    """
    mapping = {}
    lines = analysis_text.split('\n')
    in_mapping_section = False
    
    for line in lines:
        line = line.strip()
        if '## Person Mapping:' in line:
            in_mapping_section = True
            continue
        elif line.startswith('##') and in_mapping_section:
            break
        elif in_mapping_section and line.startswith('- Person'):
            # Extract mapping like "- Person A: Eric Martin"
            if ':' in line:
                person_label = line.split(':')[0].replace('- ', '').strip()
                person_name = line.split(':')[1].strip()
                mapping[person_label] = person_name
    
    return mapping

def extract_action_items(analysis_text: str) -> list[str]:
    """
    Extracts action items from analysis.
    """
    action_items = []
    lines = analysis_text.split('\n')
    in_action_section = False
    
    for line in lines:
        line = line.strip()
        if '## Action Items' in line:
            in_action_section = True
            continue
        elif line.startswith('##') and in_action_section:
            break
        elif in_action_section and line.startswith('- '):
            action_items.append(line.replace('- ', ''))
    
    return action_items

if __name__ == "__main__":
    print("⚠️  Tests have been moved to the 'tests' folder!")
    print("Run tests with:")
    print("  python tests/run_all_tests.py")
    print("  python tests/test_conversation_parser.py 3")
    print("  python tests/test_output_parser.py")
