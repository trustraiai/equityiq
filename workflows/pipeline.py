import logging
import os
import datetime

from crewai import Crew, Task
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.fundamental_agent import get_fundamental_agent
from agents.business_agent import get_business_agent
from agents.news_agent import get_news_agent
from agents.risk_agent import get_risk_agent
from agents.decision_agent import get_decision_agent
from agents.critic_agent import get_critic_agent

from utils.evaluator import evaluate_output
from tools.stock_tool import get_stock_data


# -----------------------------------
# LOGGER SETUP
# -----------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    filename=f"{LOG_DIR}/pipeline_{run_id}.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def log(message):
    print(message)
    logging.info(message)


# -----------------------------------
# SAFE AGENT RUNNER
# -----------------------------------
def run_agent(agent, description):
    try:
        log(f"🚀 Running Agent: {agent.role}")
        log(f"📌 Task: {description[:120]}...")

        task = Task(
            description=description,
            expected_output="Exactly 3 concise bullet points with insights",
            agent=agent
        )

        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()

        if hasattr(result, "raw"):
            output = result.raw
        else:
            output = str(result)

        log(f"✅ {agent.role} Output:\n{output}\n")

        return output

    except Exception as e:
        log(f"❌ ERROR in {agent.role}: {str(e)}")
        return f"ERROR: {str(e)}"


# -----------------------------------
# RETRY WRAPPER (CRITIC LOOP - LEVEL 1)
# -----------------------------------
def run_agent_with_retry(agent, description, max_retries=2):
    for attempt in range(max_retries):

        log(f"🔁 Attempt {attempt+1} for {agent.role}")

        result = run_agent(agent, description)

        eval_result = evaluate_output(result)

        if eval_result["valid"]:
            log(f"✅ {agent.role} PASSED evaluation")
            return result

        log(f"⚠️ {agent.role} FAILED evaluation → retrying")

    log(f"⚠️ {agent.role} FINAL fallback used")
    return result


# -----------------------------------
# MAIN PIPELINE
# -----------------------------------
def run_pipeline(stock_name: str):

    log(f"📊 Starting pipeline for {stock_name}")

    # -------------------------
    # STEP 1: PRE-FETCH DATA
    # -------------------------
    stock_data = get_stock_data(stock_name)
    log(f"📈 Stock Data Fetched: {stock_data}")

    # -------------------------
    # STEP 2: INIT AGENTS
    # -------------------------
    fundamental = get_fundamental_agent()
    business = get_business_agent()
    news = get_news_agent()
    risk = get_risk_agent()
    decision = get_decision_agent()
    critic = get_critic_agent()

    log("🤖 Agents initialized")

    # -------------------------
    # STEP 3: PARALLEL EXECUTION
    # -------------------------
    tasks = {
        "fundamental": (
            fundamental,
            f"""
            Analyze fundamentals using this data:
            {stock_data}

            RULES:
            - EXACTLY 3 bullet points
            - Use numbers/metrics
            - No fluff
            """
        ),
        "business": (
            business,
            f"""
            Analyze business quality of {stock_name}

            RULES:
            - EXACTLY 3 insights
            - Focus on moat, growth, management
            """
        ),
        "news": (
            news,
            f"""
            Analyze long-term news impact for {stock_name}

            IMPORTANT:
            - MUST use smart_retriever tool
            - Ignore short-term noise
            - EXACTLY 3 insights
            """
        ),
        "risk": (
            risk,
            f"""
            Identify key risks for {stock_name}

            RULES:
            - EXACTLY 3 risks
            - Be realistic, not generic
            """
        ),
    }

    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_key = {
            executor.submit(run_agent_with_retry, agent, desc): key
            for key, (agent, desc) in tasks.items()
        }

        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result(timeout=60)
                log(f"📦 Completed: {key}")
            except Exception as e:
                results[key] = f"ERROR: {str(e)}"
                log(f"❌ Error in {key}: {str(e)}")

    log(f"📊 Aggregated Results: {results}")

    # -------------------------
    # STEP 4: CRITIC ANALYSIS
    # -------------------------
    critic_task = Task(
        description=f"""
        Evaluate the following analysis:

        FUNDAMENTAL:
        {results.get("fundamental")}

        BUSINESS:
        {results.get("business")}

        NEWS:
        {results.get("news")}

        RISK:
        {results.get("risk")}

        Identify:
        - Weak reasoning
        - Missing data
        - Contradictions

        Provide short actionable feedback.
        """,
        expected_output="Concise critique with improvements",
        agent=critic
    )

    critic_crew = Crew(
        agents=[critic],
        tasks=[critic_task]
    )

    critic_result = critic_crew.kickoff()

    if hasattr(critic_result, "raw"):
        critic_feedback = critic_result.raw
    else:
        critic_feedback = str(critic_result)

    log(f"🧠 Critic Feedback:\n{critic_feedback}")

    # -------------------------
    # STEP 5: DECISION AGENT
    # -------------------------
    decision_task = Task(
        description=f"""
        Based on:

        FUNDAMENTAL:
        {results.get("fundamental")}

        BUSINESS:
        {results.get("business")}

        NEWS:
        {results.get("news")}

        RISK:
        {results.get("risk")}

        CRITIC FEEDBACK:
        {critic_feedback}

        CURRENT PRICE:
        {stock_data.get("price")}

        Provide investment recommendation.

        STRICT RULES:
        - Output ONLY valid JSON
        - No explanation outside JSON
        - No markdown
        - No extra text
        - Use realistic % ranges (10–25%)

        JSON FORMAT:
        {{
          "stock": "{stock_name}",
          "verdict": "BUY | HOLD | AVOID",
          "reasons": [],
          "risks": [],
          "confidence": "LOW | MEDIUM | HIGH",
          "buy_zone": "",
          "sell_zone": "",
          "base_case": "",
          "bull_case": "",
          "bear_case": ""
        }}
        """,
        expected_output="Strict JSON output",
        agent=decision
    )

    decision_crew = Crew(
        agents=[decision],
        tasks=[decision_task]
    )

    decision_result = decision_crew.kickoff()

    if hasattr(decision_result, "raw"):
        final_output = decision_result.raw
    else:
        final_output = str(decision_result)

    log(f"🎯 Final Decision:\n{final_output}")

    log("✅ Pipeline completed successfully")

    # -------------------------
    # FINAL RESPONSE
    # -------------------------
    return {
        "stock": stock_name,
        "analysis": results,
        "critic_feedback": critic_feedback,
        "final_decision": final_output
    }