import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)
def get_stock_data(ticker: str):
    ticker = ticker if ticker.endswith(".NS") else ticker + ".NS"
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "price": info.get("currentPrice"),
        "pe_ratio": info.get("trailingPE"),
        "roe": info.get("returnOnEquity"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margins": info.get("profitMargins"),
        "market_cap": info.get("marketCap")
    }