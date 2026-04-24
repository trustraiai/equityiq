from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_tool(query: str) -> str:
    response = client.search(query=query, search_depth="advanced")
    return "\n".join([r["content"] for r in response["results"]])