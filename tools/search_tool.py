from crewai.tools import tool
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool("Search Tool")
def search_tool(query: str) -> str:
    """Search latest news and information from the web."""
    response = client.search(query=query, max_results=5)
    return "\n".join([r["content"] for r in response["results"]])