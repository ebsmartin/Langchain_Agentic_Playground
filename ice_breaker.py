from langchain_core.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

from third_parties.linkedin import scrape_linkedin_profile

if __name__ == "__main__":
    load_dotenv()
    print("Starting LangChain...")

    summary_template = """
    Given a LinkedIn profile {profile}, I want you to do the following:
    1. Grab the full name of the person
    2. Identify the job title, description, role, or industry of the person if mentioned.
    3. Identify their education and achievements.
    4. Identify any other relevant contact information such as email, phone number, birthday, portfolio websites, or social media handles if mentioned.
    5. Summarize their most recent work experience and skills in a concise manner.
    6. Provide a list of key skills.
    7. Grab the Picture URL and Banner URL if available.
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["profile"], template=summary_template
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2,
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    chain = summary_prompt_template | llm

    res = chain.invoke(
        input={
            "profile": scrape_linkedin_profile(
                linkedin_profile_url="https://www.linkedin.com/in/ebsmartin/",
                mock=True,
            )
        }
    )
    print(res)
