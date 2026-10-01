"""
Backtesting utilities for allocation strategies.
"""

import numpy as np
import pandas as pd


def _portfolio_return(row, weights):
    return (
        row["us_equity"] * weights.get("us_equity", 0)
        + row["intl_equity"] * weights.get("intl_equity", 0)
        + row["us_bonds"] * weights.get("us_bonds", 0)
        + row["reit"] * weights.get("reit", 0)
        + row["cash"] * weights.get("cash", 0)
    ) / 100.0


def run_backtest(returns_df: pd.DataFrame, weights: dict, initial_value: float = 100000.0) -> pd.DataFrame:
    """Run annual backtest and return growth path DataFrame."""
    df = returns_df.copy()
    df["portfolio_return"] = df.apply(lambda r: _portfolio_return(r, weights), axis=1)

    values = [initial_value]
    for r in df["portfolio_return"]:
        values.append(values[-1] * (1 + r))

    out = pd.DataFrame(
        {
            "year": [df["year"].iloc[0] - 1] + df["year"].tolist(),
            "portfolio_value": values,
        }
    )

    return out


def calculate_metrics(path_df: pd.DataFrame, annual_returns: pd.Series, risk_free_rate: float = 0.02) -> dict:
    """Calculate basic backtest metrics."""
    start_val = path_df["portfolio_value"].iloc[0]
    end_val = path_df["portfolio_value"].iloc[-1]
    years = len(path_df) - 1

    cagr = (end_val / start_val) ** (1 / years) - 1 if years > 0 else 0.0
    volatility = annual_returns.std(ddof=1) if len(annual_returns) > 1 else 0.0
    sharpe = (annual_returns.mean() - risk_free_rate) / volatility if volatility > 0 else 0.0

    running_max = path_df["portfolio_value"].cummax()
    drawdowns = (path_df["portfolio_value"] - running_max) / running_max
    max_drawdown = drawdowns.min()

    return {
        "start_value": float(start_val),
        "end_value": float(end_val),
        "total_return": float((end_val / start_val) - 1),
        "cagr": float(cagr),
        "volatility": float(volatility),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_drawdown),
    }


def compare_strategies(returns_df: pd.DataFrame, strategies: dict, initial_value: float = 100000.0):
    """Run multiple strategies and return paths + metrics."""
    all_paths = []
    metrics_rows = []

    for name, weights in strategies.items():
        path_df = run_backtest(returns_df, weights, initial_value)
        annual_returns = returns_df.apply(lambda r: _portfolio_return(r, weights), axis=1)
        metrics = calculate_metrics(path_df, annual_returns)
        metrics["strategy"] = name

        p = path_df.copy()
        p["strategy"] = name
        all_paths.append(p)
        metrics_rows.append(metrics)

    return pd.concat(all_paths, ignore_index=True), pd.DataFrame(metrics_rows)
