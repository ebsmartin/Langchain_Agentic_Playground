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
    
    # Updated template to handle search queries properly
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
    
    Output Expected: Only provide a LinkedIn URL as your output.
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
            - Input: "Matt software engineer Nickel5" → Search for: "Matt software engineer Nickel5"  
            - Input: "John Smith Google" → Search for: "John Smith Google"
            
            The search query may contain name + job title + company information.
            """,
        )
    ]

    react_prompt = hub.pull("hwchase17/react")  # pulled from LangChain Hub

    agent = create_react_agent(
        llm=llm,
        prompt=react_prompt,
        tools=tools_for_agent,
    )

    # Add handle_parsing_errors=True to fix the parsing issue
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools_for_agent, 
        verbose=True,
        handle_parsing_errors=True,  # This fixes the parsing error
        max_iterations=3
    )

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(query=query)}
    )
    
    # Extract LinkedIn URL from the result
    output = result["output"]
    if "linkedin.com/in/" in output:
        import re
        urls = re.findall(r'https://www\.linkedin\.com/in/[^\s\)]+', output)
        if urls:
            return urls[0]
    
    return f"Could not find a LinkedIn profile for the query: {query}"


if __name__ == "__main__":
    linkedin_url = lookup("Eric Burton Martin Cognizant")
    print(f"LinkedIn Profile URL: {linkedin_url}")
