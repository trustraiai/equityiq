from crewai import Agent

def get_risk_agent():
    return Agent(
        role="Risk Analyst",
        goal="Identify long-term risks in business and sector",
        backstory="Expert in risk evaluation"
    )