import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
# This allows imports from sibling directories like 'tools'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import Tool
from langchain.agents import (
    create_react_agent,
    AgentExecutor,
)
from langchain import hub
from tools.tools import get_profile_url_tavily


def lookup(query: str) -> str:
    """
    Looks up a LinkedIn profile by search query containing name and/or other details.
    
    Args:
        query (str): Search query containing person's name, job title, company, etc.
                    Examples: "Eric Burton Martin Cognizant", "Matt software engineer Nickel5"
    """
    # Debug: Check if API key is loaded (remove this after testing)
    api_key = os.environ.get("OPENAI_API_KEY")
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")
    print(f"First 10 chars: {api_key[:10] if api_key else 'None'}")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=api_key,
    )
    
    # Updated template to handle search queries properly and specify clean output format
    template = """ 
    Given the search query: "{query}"
    
    This search query contains information about a person that may include:
    - Their first name or full name
    - Their job title or role
    - Their company or workplace
    - Other identifying information
    
    Use this information to find their LinkedIn profile page. 
    
    IMPORTANT: Do NOT assume the entire query is a full name. Parse it to identify:
    - The person's actual name (usually the first word or two)
    - Their job/company details (use as search context)
    
    For example:
    - "Matt software engineer Nickel5" → Search for "Matt" who is a "software engineer" at "Nickel5"
    - "John Smith Google" → Search for "John Smith" at "Google"
    - "Sarah marketing director" → Search for "Sarah" who is a "marketing director"
    
    Output Expected: Only provide a clean LinkedIn URL as your output.
    
    IMPORTANT OUTPUT FORMAT:
    - Return ONLY the URL, nothing else
    - Do NOT use markdown formatting like [text](url)
    - Do NOT add explanatory text
    - Just return: https://www.linkedin.com/in/username
    """

    prompt_template = PromptTemplate(template=template, input_variables=["query"])

    tools_for_agent = [
        Tool(
            name="Search Google for LinkedIn Profile URL",
            func=get_profile_url_tavily,
            description="""
            Searches for LinkedIn profile URLs using the provided search query.
            
            IMPORTANT: Use the search query EXACTLY as provided. Do not modify it.
            
            Examples:
            - Input: "Matt software engineer Nickel5 linkedin" → Search for: "Matt software engineer Nickel5 linkedin"  
            - Input: "John Smith Google LinkedIn" → Search for: "John Smith Google LinkedIn"
            
            The search query may contain first name + job title + company information + linkedin in no particular order.
            """,
        )
    ]

    react_prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(
        llm=llm,
        prompt=react_prompt,
        tools=tools_for_agent,
    )

    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools_for_agent, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Increased from 3 to 5
        early_stopping_method="generate"  # Stop early when goal is achieved
    )

    try:
        result = agent_executor.invoke(
            input={"input": prompt_template.format_prompt(query=query)}
        )
        
        # Extract and clean LinkedIn URL from the result
        output = result["output"].strip()
        
        # Debug: Show raw agent output
        print(f"🔗 Raw agent output: '{output}'")
        
        # Handle iteration limit case - check if URL was found in intermediate steps
        if "Agent stopped due to iteration limit" in output or "time limit" in output:
            print("⚠️ Agent hit iteration limit, checking intermediate steps...")
            
            # Try to extract URL from the agent's intermediate steps
            if hasattr(result, 'intermediate_steps'):
                for step in result['intermediate_steps']:
                    if len(step) > 1 and isinstance(step[1], str):
                        step_output = step[1]
                        if 'linkedin.com/in/' in step_output and 'Found LinkedIn URL:' in step_output:
                            # Extract URL from step output
                            import re
                            urls = re.findall(r'https://www\.linkedin\.com/in/[^\s\)\]<>"\']+', step_output)
                            if urls:
                                found_url = urls[0].rstrip('.,;)')
                                print(f"🎯 Recovered URL from intermediate steps: {found_url}")
                                output = found_url
                                break
        
        # Clean up malformed URLs and markdown formatting
        linkedin_url = output
        
        # Fix markdown-style malformed URLs
        if '](https://' in linkedin_url:
            print("🧹 Detected markdown formatting, cleaning...")
            if linkedin_url.startswith('[') and '](https://www.linkedin.com/in/' in linkedin_url:
                url_part = linkedin_url.split('](')[1]
                if url_part.endswith(')'):
                    url_part = url_part[:-1]
                linkedin_url = url_part
            else:
                if '](https://www.linkedin.com/in/' in linkedin_url:
                    linkedin_url = linkedin_url.split('](')[1]
                    if linkedin_url.endswith(')'):
                        linkedin_url = linkedin_url[:-1]
        
        # Remove any leading/trailing brackets or markdown artifacts
        linkedin_url = linkedin_url.strip('[](){}"\'')
        
        # If the above cleaning didn't work, try regex extraction as fallback
        if "linkedin.com/in/" in linkedin_url:
            import re
            urls = re.findall(r'https://www\.linkedin\.com/in/[^\s\)\]<>"\']+', linkedin_url)
            if urls:
                linkedin_url = urls[0]
                # Clean trailing punctuation
                linkedin_url = linkedin_url.rstrip('.,;)')
        
        # Validate the final URL
        if linkedin_url.startswith("http") and "linkedin.com/in/" in linkedin_url:
            print(f"🔗 Cleaned LinkedIn URL: {linkedin_url}")
            return linkedin_url
    
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        # Try direct search as fallback
        try:
            print("🔄 Attempting direct search fallback...")
            direct_result = get_profile_url_tavily(query)
            if direct_result and "linkedin.com/in/" in direct_result:
                print(f"🎯 Direct search found: {direct_result}")
                return direct_result
        except Exception as e2:
            print(f"❌ Direct search also failed: {e2}")
    
    return f"Could not find a LinkedIn profile for the query: {query}"

if __name__ == "__main__":
    linkedin_url = lookup("Eric Burton Martin Cognizant")
    print(f"LinkedIn Profile URL: {linkedin_url}")
