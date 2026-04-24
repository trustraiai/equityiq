from crewai import Agent
from tools.search import search_tool
from tools.finance import stock_tool
from memory.vector_store import retrieve_data, store_data

def smart_tool(query: str):
    memory = retrieve_data(query)
    web = search_tool(query)

    combined = f"""
    MEMORY:
    {memory}

    WEB:
    {web}
    """

    store_data(combined)
    return combined

researcher = Agent(
    role="Researcher",
    goal="Find accurate, real-time and contextual data",
    backstory="Expert in web + financial + historical data",
    tools=[smart_tool, stock_tool],
    verbose=True
)