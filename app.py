"""
Asset Allocation Backtester - advisor workflow Streamlit app.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from calculators.backtest import compare_strategies, validate_weights
from data.sample_returns import SAMPLE_RETURNS

st.set_page_config(page_title="Asset Allocation Backtester", page_icon="📈", layout="wide")

st.title("📈 Asset Allocation Backtester")
st.markdown("Compare allocation strategies with annual rebalance versus buy-and-hold behavior.")

returns_df = pd.DataFrame(SAMPLE_RETURNS)

st.sidebar.header("Backtest Settings")
initial_value = st.sidebar.number_input(
    "Initial Portfolio Value ($)", min_value=10000, max_value=5000000, value=250000, step=10000
)
risk_free_rate = st.sidebar.slider("Risk-Free Rate (%)", min_value=0.0, max_value=8.0, value=2.0, step=0.1) / 100
rebalance_mode = st.sidebar.radio("Allocation Handling", options=["annual", "buy-and-hold"], index=0)


def allocation_block(title: str, prefix: str, defaults: dict):
    st.sidebar.subheader(title)
    us = st.sidebar.slider(f"{prefix} US Equity", 0, 100, defaults["us_equity"])
    intl = st.sidebar.slider(f"{prefix} Intl Equity", 0, 100, defaults["intl_equity"])
    bonds = st.sidebar.slider(f"{prefix} US Bonds", 0, 100, defaults["us_bonds"])
    reit = st.sidebar.slider(f"{prefix} REIT", 0, 100, defaults["reit"])
    cash = st.sidebar.slider(f"{prefix} Cash", 0, 100, defaults["cash"])
    weights = {
        "us_equity": us,
        "intl_equity": intl,
        "us_bonds": bonds,
        "reit": reit,
        "cash": cash,
    }
    is_valid, err = validate_weights(weights)
    total = sum(weights.values())
    if is_valid:
        st.sidebar.caption(f"{prefix} allocation total: {total:.0f}%")
    else:
        st.sidebar.warning(f"{prefix}: {err}")
    return weights, is_valid


s1, s1_valid = allocation_block(
    "Strategy 1: 60/40 Core", "S1", {"us_equity": 45, "intl_equity": 15, "us_bonds": 35, "reit": 5, "cash": 0}
)
s2, s2_valid = allocation_block(
    "Strategy 2: Growth Tilt", "S2", {"us_equity": 60, "intl_equity": 20, "us_bonds": 15, "reit": 5, "cash": 0}
)
s3, s3_valid = allocation_block(
    "Strategy 3: Defensive", "S3", {"us_equity": 30, "intl_equity": 10, "us_bonds": 50, "reit": 5, "cash": 5}
)

strategies = {
    "60/40 Core": s1,
    "Growth Tilt": s2,
    "Defensive": s3,
}

if st.sidebar.button("Run Backtest", use_container_width=True):
    if not (s1_valid and s2_valid and s3_valid):
        st.error("Each strategy must total 100% allocation.")
    else:
        paths_df, metrics_df, annual_returns_df = compare_strategies(
            returns_df,
            strategies,
            initial_value=initial_value,
            rebalance_mode=rebalance_mode,
            risk_free_rate=risk_free_rate,
        )
        st.session_state.paths_df = paths_df
        st.session_state.metrics_df = metrics_df
        st.session_state.annual_returns_df = annual_returns_df
        st.session_state.rebalance_mode = rebalance_mode

if "paths_df" in st.session_state:
    paths_df = st.session_state.paths_df
    metrics_df = st.session_state.metrics_df
    annual_returns_df = st.session_state.annual_returns_df

    st.subheader("Growth of Portfolio Value")
    growth_fig = px.line(
        paths_df,
        x="year",
        y="portfolio_value",
        color="strategy",
        title=f"Portfolio Growth Comparison ({st.session_state.rebalance_mode})",
    )
    growth_fig.update_layout(yaxis_title="Portfolio Value ($)", xaxis_title="Year")
    st.plotly_chart(growth_fig, use_container_width=True)

    st.subheader("Annual Return Comparison")
    bar_fig = px.bar(
        annual_returns_df,
        x="year",
        y="annual_return",
        color="strategy",
        barmode="group",
        title="Annual Portfolio Returns by Strategy",
    )
    bar_fig.update_layout(yaxis_tickformat=".1%", yaxis_title="Annual Return", xaxis_title="Year")
    st.plotly_chart(bar_fig, use_container_width=True)

    st.subheader("Performance Metrics")
    display = metrics_df.copy()
    pct_cols = ["total_return", "cagr", "volatility", "max_drawdown", "best_year", "worst_year", "positive_year_ratio"]
    for col in pct_cols:
        display[col] = (display[col] * 100).map(lambda x: f"{x:.1f}%")

    display["sharpe"] = display["sharpe"].map(lambda x: f"{x:.2f}")
    display["calmar"] = display["calmar"].map(lambda x: f"{x:.2f}")
    display["start_value"] = display["start_value"].map(lambda x: f"${x:,.0f}")
    display["end_value"] = display["end_value"].map(lambda x: f"${x:,.0f}")

    st.dataframe(
        display[
            [
                "strategy",
                "start_value",
                "end_value",
                "total_return",
                "cagr",
                "volatility",
                "max_drawdown",
                "sharpe",
                "calmar",
                "best_year",
                "worst_year",
                "positive_year_ratio",
            ]
        ],
        use_container_width=True,
    )
else:
    st.info("Set strategy weights and click Run Backtest.")

st.divider()
st.caption("Uses embedded annual return samples for advisor workflow prototyping.")
