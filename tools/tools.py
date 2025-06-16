from langchain_community.tools.tavily_search import TavilySearchResults
import os


def get_profile_url_tavily(name: str) -> str:
    """
    Looks up a LinkedIn profile by name using Tavily Search.
    """
    search = TavilySearchResults(tavily_api_key=os.environ.get("TAVILY_API_KEY"))

    results = search.run(f"{name}")

    if not results:
        raise ValueError("No LinkedIn profile found for the given name.")

    return results
