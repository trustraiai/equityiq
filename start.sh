#!/bin/bash

echo "🚀 Starting EquityAI setup..."

# -----------------------------
# STEP 1: CREATE VENV (if not exists)
# -----------------------------
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# -----------------------------
# STEP 2: ACTIVATE VENV
# -----------------------------
source venv/bin/activate

# -----------------------------
# STEP 3: INSTALL DEPENDENCIES
# -----------------------------
pip install --upgrade pip > /dev/null

pip install \
    crewai \
    "crewai[tools]" \
    langchain \
    langchain-core \
    langchain-community \
    langchain-openai \
    streamlit \
    tavily-python \
    yfinance \
    pandas \
    ta \
    plotly \
    python-dotenv \
    chromadb > /dev/null

echo "📦 Dependencies ready"

# -----------------------------
# STEP 4: START APPS (WITH LOGS)
# -----------------------------
echo "🚀 Starting apps..."

# kill old processes
pkill -f "streamlit run" 2>/dev/null

# start apps with logs
streamlit run app.py --server.port 8501 > app.log 2>&1 &
APP_PID=$!

streamlit run admin_dashboard.py --server.port 8502 > admin.log 2>&1 &
ADMIN_PID=$!

sleep 3

# -----------------------------
# STEP 5: VERIFY
# -----------------------------
echo ""
echo "🔍 Checking services..."

if lsof -i :8501 > /dev/null; then
    echo "✅ Customer App running at http://localhost:8501"
else
    echo "❌ Customer App failed. Check app.log"
fi

if lsof -i :8502 > /dev/null; then
    echo "✅ Admin Dashboard running at http://localhost:8502"
else
    echo "❌ Admin Dashboard failed. Check admin.log"
fi

echo ""
echo "📜 Logs:"
echo "👉 tail -f app.log"
echo "👉 tail -f admin.log"
echo ""

wait