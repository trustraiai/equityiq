from crewai import Agent
from tools.smart_retriever import smart_retriever


def get_news_agent():
    return Agent(
        role="News Analyst",
        goal="Analyze long-term impact using real-time and historical data",
        backstory="Expert in combining memory and live data",
        tools=[smart_retriever],   # ✅ NOW VALID
        verbose=True
    )