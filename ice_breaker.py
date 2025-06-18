from langchain_core.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

from third_parties.linkedin import scrape_linkedin_profile
from agents import linkedin_lookup_agent
from output_parsers import summary_parser, Summary

def ice_break_with(name: str, mock=True) -> tuple [Summary, str, str]:
    """
    Looks up a LinkedIn profile by name and returns a summary.
    """
    if mock:
        # Skip lookup when using mock data
        linkedin_url = "https://www.linkedin.com/in/dummy"
    else:
        linkedin_url = linkedin_lookup_agent.lookup(name=name)
    
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_url, mock=mock)
    
    # Debug: Print available keys to understand the data structure
    print("=== DEBUG: LinkedIn Data Keys ===")
    print(f"Available keys: {list(linkedin_data.keys()) if isinstance(linkedin_data, dict) else 'Not a dict'}")
    
    # Extract the person data from the API response
    person_data = linkedin_data.get('person', {}) if isinstance(linkedin_data, dict) else {}
    
    # Extract image URLs from the person data using the correct field names
    profile_picture_url = person_data.get('photoUrl')
    banner_url = person_data.get('backgroundUrl')
    
    # Add the extracted URLs to the main data
    if profile_picture_url:
        linkedin_data['profile_picture_url'] = profile_picture_url
    if banner_url:
        linkedin_data['banner_url'] = banner_url
    
    # Debug: Print what image URLs were found
    print("=== DEBUG: Extracted Image URLs ===")
    print(f"Profile Picture: {profile_picture_url}")
    print(f"Banner: {banner_url}")

    summary_template = """
    Given a LinkedIn profile {profile}, I want you to do the following:
    1. Grab the full name of the person
    2. Identify the job title, description, role, or industry of the person if mentioned.
    3. Identify their education and achievements.
    4. Identify any other relevant contact information such as email, phone number, birthday, portfolio websites, or social media handles if mentioned.
    5. Summarize their most recent work experience and skills in a concise manner.
    6. Provide a list of key skills.
    7. Grab the Picture URL and Banner URL if available.

    \n{format_instructions}
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["profile"], 
        template=summary_template, 
        partial_variables={"format_instructions": summary_parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2,
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    chain = summary_prompt_template | llm | summary_parser

    res:Summary = chain.invoke(
        input={
            "profile": linkedin_data
        }
    )
    print(res)
    return res, linkedin_data.get('profile_picture_url'), linkedin_data.get('banner_url')

if __name__ == "__main__":
    load_dotenv()
    print("Ice Breaker Started")
    ice_break_with("Eric Burton Martin Cognizant", mock=False)
    print("Ice Breaker Completed")


