import streamlit as st
import json
import yfinance as yf
import plotly.graph_objects as go
import time
import numpy as np

from workflows.pipeline import run_pipeline

# -------------------------
# LOAD CSS
# -------------------------
def load_css():
    with open("styles/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="EquityIQ 🇮🇳", layout="wide")

load_css()

# -------------------------
# HEADER (CENTERED)
# -------------------------
st.markdown("<div class='center-title'>📊 EquityIQ 🇮🇳</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='center-sub'>AI-powered long-term investment insights. Not financial advice.</div>",
    unsafe_allow_html=True
)

# -------------------------
# INPUT CARD (FIXED)
# -------------------------
with st.container():
   # st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])

    with col1:
        stock = st.text_input(
            "Enter Stock",
            placeholder="RELIANCE, TCS, INFY",
            label_visibility="collapsed"
        )

    with col2:
        analyze = st.button("Analyze")

   

# -------------------------
# HELPERS
# -------------------------
def get_stock_info(ticker):
    ticker = ticker if ticker.endswith(".NS") else ticker + ".NS"
    stock = yf.Ticker(ticker)
    return stock.history(period="6mo")

def generate_forecast(price, verdict, hist):
    returns = hist["Close"].pct_change().dropna()
    if returns.empty:
        return {}

    volatility = returns.std()
    drift_map = {"BUY": 0.001, "HOLD": 0.0003, "AVOID": -0.001}
    drift = drift_map.get(verdict, 0)

    timeframes = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
    forecast = {}

    for tf, days in timeframes.items():
        expected_return = drift * days
        uncertainty = volatility * np.sqrt(days)

        low = price * (1 + expected_return - uncertainty)
        high = price * (1 + expected_return + uncertainty)

        forecast[tf] = {
            "range": f"₹{round(low)} - ₹{round(high)}",
            "change": f"{round(expected_return*100,1):+}%"
        }

    return forecast

def monte_carlo(price, hist, simulations=500, days=252):
    returns = hist["Close"].pct_change().dropna()
    if returns.empty:
        return {}

    mu = returns.mean()
    sigma = returns.std()

    results = []

    for _ in range(simulations):
        prices = [price]
        for _ in range(days):
            shock = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + shock))
        results.append(prices[-1])

    results = np.array(results)

    return {
        "p10": round(np.percentile(results, 10)),
        "p50": round(np.percentile(results, 50)),
        "p90": round(np.percentile(results, 90))
    }

def calculate_rsi(hist, period=14):
    delta = hist["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

# -------------------------
# MAIN FLOW
# -------------------------
if analyze:

    if not stock:
        st.warning("Please enter a stock name")
        st.stop()

    with st.spinner("🧑‍💻 Agents at work ⚡📊"):
        start = time.time()
        result = run_pipeline(stock)
        response_time = round(time.time() - start, 2)

    st.markdown(
        f"<div class='success-box'>Analysis Complete in {response_time}s</div>",
        unsafe_allow_html=True
    )

    hist = get_stock_info(stock)
    valid_prices = hist["Close"].dropna()

    if valid_prices.empty:
        st.error("No price data available")
        st.stop()

    current_price = round(float(valid_prices.iloc[-1]), 2)

    try:
        final = json.loads(result["final_decision"])
    except:
        final = {}

    verdict = final.get("verdict", "N/A")
    confidence = final.get("confidence", "N/A")

    forecast = generate_forecast(current_price, verdict, hist)
    mc = monte_carlo(current_price, hist)
    rsi = calculate_rsi(hist)

    # -------------------------
    # SUMMARY
    # -------------------------
    if final:
       # st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🧠 AI Summary</div>", unsafe_allow_html=True)
        st.write(f"**Verdict:** {verdict} | **Confidence:** {confidence}")
        st.metric("Current Price", f"₹{current_price}")

       # st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # FORECAST
    # -------------------------
    st.markdown("<div class='section-title'>📊 Forecast</div>", unsafe_allow_html=True)

    cols = st.columns(5)
    for i, tf in enumerate(["1W", "1M", "3M", "6M", "1Y"]):
        data = forecast.get(tf, {})
        cols[i].metric(tf, data.get("range", "-"), data.get("change", ""))

    # -------------------------
    # MONTE CARLO
    # -------------------------
    st.markdown("<div class='section-title'>🎲 Monte Carlo</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Worst", f"₹{mc.get('p10')}")
    col2.metric("Median", f"₹{mc.get('p50')}")
    col3.metric("Best", f"₹{mc.get('p90')}")

    # -------------------------
    # RSI
    # -------------------------
    st.markdown("<div class='section-title'>⏱ Entry Timing</div>", unsafe_allow_html=True)

    if rsi < 30:
        st.success(f"RSI {rsi} → Buy Opportunity")
    elif rsi > 70:
        st.error(f"RSI {rsi} → Overbought")
    else:
        st.warning(f"RSI {rsi} → Neutral")

    # -------------------------
    # PROS / RISKS (RESTORED)
    # -------------------------
    st.markdown("<div class='section-title'>⚖️ Investment Breakdown</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Pros")
        for r in final.get("reasons", []):
            st.write(f"- {r}")

    with col2:
        st.markdown("### ⚠️ Risks")
        for r in final.get("risks", []):
            st.write(f"- {r}")

    # -------------------------
    # CHART
    # -------------------------
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines'))
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)