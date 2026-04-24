from crewai import Agent
from tools.search_tool import search_tool

def get_business_agent():
    return Agent(
        role="Business Analyst",
        goal="Analyze business quality and growth",
        backstory="Expert in industry analysis",
        tools=[search_tool]
    )