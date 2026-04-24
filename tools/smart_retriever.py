from crewai.tools import tool
from tools.memory_tool import retrieve_memory, store_memory
from tools.search import search_tool


@tool("smart_retriever")
def smart_retriever(query: str) -> str:
    """Fetch data using memory + web search"""

    memory = retrieve_memory(query)
    web = search_tool(query)

    combined = f"""
    MEMORY:
    {memory}

    WEB:
    {web}
    """

    store_memory(combined)

    return combined