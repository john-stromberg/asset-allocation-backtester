"""
Asset Allocation Backtester - MVP Streamlit app.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from calculators.backtest import compare_strategies
from data.sample_returns import SAMPLE_RETURNS

st.set_page_config(page_title="Asset Allocation Backtester", page_icon="📈", layout="wide")

st.title("📈 Asset Allocation Backtester")
st.markdown("Compare portfolio allocation strategies using sample historical-style annual returns.")

returns_df = pd.DataFrame(SAMPLE_RETURNS)

st.sidebar.header("Backtest Settings")
initial_value = st.sidebar.number_input("Initial Portfolio Value ($)", min_value=10000, max_value=5000000, value=100000, step=10000)

st.sidebar.subheader("Strategy 1: 60/40 Core")
s1_us = st.sidebar.slider("S1 US Equity", 0, 100, 45)
s1_intl = st.sidebar.slider("S1 Intl Equity", 0, 100, 15)
s1_bonds = st.sidebar.slider("S1 US Bonds", 0, 100, 35)
s1_reit = st.sidebar.slider("S1 REIT", 0, 100, 5)
s1_cash = st.sidebar.slider("S1 Cash", 0, 100, 0)

st.sidebar.subheader("Strategy 2: Growth Tilt")
s2_us = st.sidebar.slider("S2 US Equity", 0, 100, 60)
s2_intl = st.sidebar.slider("S2 Intl Equity", 0, 100, 20)
s2_bonds = st.sidebar.slider("S2 US Bonds", 0, 100, 15)
s2_reit = st.sidebar.slider("S2 REIT", 0, 100, 5)
s2_cash = st.sidebar.slider("S2 Cash", 0, 100, 0)

st.sidebar.subheader("Strategy 3: Defensive")
s3_us = st.sidebar.slider("S3 US Equity", 0, 100, 30)
s3_intl = st.sidebar.slider("S3 Intl Equity", 0, 100, 10)
s3_bonds = st.sidebar.slider("S3 US Bonds", 0, 100, 50)
s3_reit = st.sidebar.slider("S3 REIT", 0, 100, 5)
s3_cash = st.sidebar.slider("S3 Cash", 0, 100, 5)

def normalize(weights):
    total = sum(weights.values())
    if total == 0:
        return {k: 0 for k in weights}
    return {k: v / total for k, v in weights.items()}

strategies = {
    "60/40 Core": normalize({"us_equity": s1_us, "intl_equity": s1_intl, "us_bonds": s1_bonds, "reit": s1_reit, "cash": s1_cash}),
    "Growth Tilt": normalize({"us_equity": s2_us, "intl_equity": s2_intl, "us_bonds": s2_bonds, "reit": s2_reit, "cash": s2_cash}),
    "Defensive": normalize({"us_equity": s3_us, "intl_equity": s3_intl, "us_bonds": s3_bonds, "reit": s3_reit, "cash": s3_cash}),
}

if st.sidebar.button("Run Backtest", use_container_width=True):
    paths_df, metrics_df = compare_strategies(returns_df, strategies, initial_value)
    st.session_state.paths_df = paths_df
    st.session_state.metrics_df = metrics_df

if "paths_df" in st.session_state:
    paths_df = st.session_state.paths_df
    metrics_df = st.session_state.metrics_df

    st.subheader("Growth of Portfolio Value")
    fig = px.line(paths_df, x="year", y="portfolio_value", color="strategy", title="Portfolio Growth Comparison")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Performance Metrics")
    display = metrics_df.copy()
    display["total_return"] = (display["total_return"] * 100).map(lambda x: f"{x:.1f}%")
    display["cagr"] = (display["cagr"] * 100).map(lambda x: f"{x:.2f}%")
    display["volatility"] = (display["volatility"] * 100).map(lambda x: f"{x:.2f}%")
    display["max_drawdown"] = (display["max_drawdown"] * 100).map(lambda x: f"{x:.1f}%")
    display["sharpe"] = display["sharpe"].map(lambda x: f"{x:.2f}")
    display["start_value"] = display["start_value"].map(lambda x: f"${x:,.0f}")
    display["end_value"] = display["end_value"].map(lambda x: f"${x:,.0f}")

    st.dataframe(display[["strategy", "start_value", "end_value", "total_return", "cagr", "volatility", "max_drawdown", "sharpe"]], use_container_width=True)
else:
    st.info("Set strategy weights and click Run Backtest.")

st.divider()
st.caption("MVP uses embedded sample return series for demonstration and advisor workflow prototyping.")
