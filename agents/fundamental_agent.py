from crewai import Agent

def get_fundamental_agent():
    return Agent(
        role="Fundamental Analyst",
        goal="Analyze financial metrics",
        backstory="Expert in financial statement analysis",
        verbose=False
    )