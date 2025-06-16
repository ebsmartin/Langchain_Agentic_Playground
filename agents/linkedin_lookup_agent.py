import os
import sys
from dotenv import load_dotenv

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


def lookup(name: str) -> str:
    """
    Looks up a LinkedIn profile by name.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
    )
    template = """ Given the full name {name}, I want you to find the link to their LinkedIn profile page. 
                    Output Expected: Only provide a URL as your output."""

    prompt_template = PromptTemplate(template=template, input_variables=["name"])

    tools_for_agent = [
        Tool(
            name="Search Google for LinkedIn Profile URL",
            func=get_profile_url_tavily,
            description="Looks up a LinkedIn profile by name.",
        )
    ]

    react_prompt = hub.pull("hwchase17/react")  # pulled from LangChain Hub

    agent = create_react_agent(
        llm=llm,
        prompt=react_prompt,
        tools=tools_for_agent,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_for_agent,
        verbose=True,
    )

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(name=name)}
    )

    linkedin_profile_url = result["output"].strip()
    if not linkedin_profile_url.startswith("http"):
        raise ValueError("Invalid LinkedIn profile URL returned.")
    return linkedin_profile_url


if __name__ == "__main__":
    linkedin_url = lookup("Eric Burton Martin Cognizant")
    print(f"LinkedIn Profile URL: {linkedin_url}")
