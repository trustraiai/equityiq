import streamlit as st
import os
import json
import glob

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# -------------------------
# SIMPLE AUTH
# -------------------------
ADMIN_PASSWORD = "admin123"  # change this!

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter Admin Password", type="password")

    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()

# -------------------------
# ADMIN DASHBOARD
# -------------------------
st.title("🛠 Admin Observability Dashboard")

# -------------------------
# LOG FILES
# -------------------------
st.sidebar.header("📜 Logs")

log_files = sorted(glob.glob("logs/*.log"), reverse=True)

if not log_files:
    st.warning("No logs found")
    st.stop()

selected_log = st.sidebar.selectbox("Select Log File", log_files)

# -------------------------
# READ LOG CONTENT
# -------------------------
with open(selected_log, "r") as f:
    logs = f.readlines()

# -------------------------
# DISPLAY LOGS
# -------------------------
st.subheader("📄 Raw Logs")

st.text_area("Logs", "".join(logs), height=300)

# -------------------------
# PARSE METRICS FROM LOG
# -------------------------
st.subheader("📊 Parsed Metrics")

agent_metrics = []
total_time = None
total_cost = None
total_tokens = None

for line in logs:
    if "Time:" in line and "Tokens:" in line:
        agent_metrics.append(line.strip())

    if "Total Time:" in line:
        total_time = line.strip()

    if "Total Cost:" in line:
        total_cost = line.strip()

    if "Total Tokens:" in line:
        total_tokens = line.strip()

# -------------------------
# SHOW METRICS
# -------------------------
col1, col2, col3 = st.columns(3)

col1.write(total_time or "No data")
col2.write(total_tokens or "No data")
col3.write(total_cost or "No data")

st.divider()

# -------------------------
# AGENT METRICS
# -------------------------
st.subheader("🤖 Agent Metrics")

for metric in agent_metrics:
    st.write(metric)

# -------------------------
# FILTER VIEW
# -------------------------
st.subheader("🔍 Filter Logs")

filter_text = st.text_input("Search logs")

if filter_text:
    filtered = [line for line in logs if filter_text.lower() in line.lower()]
    st.text_area("Filtered Logs", "".join(filtered), height=300)