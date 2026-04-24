from crewai import Agent

def get_decision_agent():
    return Agent(
        role="Investment Advisor",
        goal="""
        Provide final recommendation in STRICT format:
        {
          "stock": "<name>",
          "verdict": "BUY | HOLD | AVOID",
          "horizon": "3-5 years",
          "reasons": ["point1", "point2"],
          "risks": ["risk1", "risk2"],
          "confidence": "LOW | MEDIUM | HIGH"
        }

        Do not return anything outside this JSON.
        """,
        backstory="Serious long-term investor"
    )