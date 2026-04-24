from crewai import Agent

def get_critic_agent():
    return Agent(
        role="Senior Investment Analyst",
        goal="Evaluate quality and accuracy of analysis",
        backstory="Expert in validating financial insights and detecting weak reasoning",
        verbose=True
    )