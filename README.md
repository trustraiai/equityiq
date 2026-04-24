# 📊 AI Stock Advisor (India)

A multi-agent AI system that analyzes Indian stocks using fundamental, business, news, and risk perspectives.

## 🚀 Features
- Multi-agent analysis (CrewAI)
- Parallel execution (fast)
- AI decision (BUY / HOLD / AVOID)
- Critic feedback loop
- Streamlit dashboard

## 🧠 Architecture
User → Agents → Decision → Critic → Improved Output → UI

## ⚙️ Tech Stack
- Python
- CrewAI
- Streamlit
- yfinance
- Tavily API

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py