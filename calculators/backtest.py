"""
Backtesting utilities for allocation strategies.
"""

import pandas as pd

ASSET_COLUMNS = ["us_equity", "intl_equity", "us_bonds", "reit", "cash"]


def normalize_weights(weights: dict) -> dict:
    total = sum(weights.values())
    if total <= 0:
        return {k: 0.0 for k in ASSET_COLUMNS}
    return {k: float(weights.get(k, 0.0)) / float(total) for k in ASSET_COLUMNS}


def validate_weights(weights: dict) -> tuple[bool, str]:
    total = sum(weights.values())
    if total <= 0:
        return False, "Allocation total must be greater than 0%."
    if abs(total - 100.0) > 0.1:
        return False, f"Allocation totals {total:.1f}%. It should total 100%."
    return True, ""


def run_backtest(
    returns_df: pd.DataFrame,
    weights: dict,
    initial_value: float = 100000.0,
    rebalance_mode: str = "annual",
) -> tuple[pd.DataFrame, pd.Series]:
    """Run annual backtest and return growth path plus annual returns series."""
    df = returns_df.copy().sort_values("year").reset_index(drop=True)
    target = normalize_weights(weights)

    values = [initial_value]
    annual_returns = []
    holdings = {asset: initial_value * target[asset] for asset in ASSET_COLUMNS}

    for _, row in df.iterrows():
        if rebalance_mode == "annual":
            total_before = sum(holdings.values())
            holdings = {asset: total_before * target[asset] for asset in ASSET_COLUMNS}

        for asset in ASSET_COLUMNS:
            holdings[asset] = holdings[asset] * (1 + (row[asset] / 100.0))

        total_after = sum(holdings.values())
        annual_returns.append((total_after / values[-1]) - 1)
        values.append(total_after)

    path_df = pd.DataFrame(
        {
            "year": [df["year"].iloc[0] - 1] + df["year"].tolist(),
            "portfolio_value": values,
        }
    )

    return path_df, pd.Series(annual_returns, name="portfolio_return")


def calculate_metrics(path_df: pd.DataFrame, annual_returns: pd.Series, risk_free_rate: float = 0.02) -> dict:
    """Calculate backtest metrics for advisor comparisons."""
    start_val = float(path_df["portfolio_value"].iloc[0])
    end_val = float(path_df["portfolio_value"].iloc[-1])
    years = max(len(path_df) - 1, 1)

    cagr = (end_val / start_val) ** (1 / years) - 1
    volatility = float(annual_returns.std(ddof=1)) if len(annual_returns) > 1 else 0.0
    sharpe = ((float(annual_returns.mean()) - risk_free_rate) / volatility) if volatility > 0 else 0.0

    running_max = path_df["portfolio_value"].cummax()
    drawdowns = (path_df["portfolio_value"] - running_max) / running_max
    max_drawdown = float(drawdowns.min())
    calmar = (cagr / abs(max_drawdown)) if max_drawdown < 0 else 0.0

    positive_years = float((annual_returns > 0).sum()) / float(len(annual_returns)) if len(annual_returns) else 0.0

    return {
        "start_value": start_val,
        "end_value": end_val,
        "total_return": float((end_val / start_val) - 1),
        "cagr": float(cagr),
        "volatility": volatility,
        "sharpe": float(sharpe),
        "max_drawdown": max_drawdown,
        "calmar": float(calmar),
        "best_year": float(annual_returns.max()) if len(annual_returns) else 0.0,
        "worst_year": float(annual_returns.min()) if len(annual_returns) else 0.0,
        "positive_year_ratio": positive_years,
    }


def compare_strategies(
    returns_df: pd.DataFrame,
    strategies: dict,
    initial_value: float = 100000.0,
    rebalance_mode: str = "annual",
    risk_free_rate: float = 0.02,
):
    """Run multiple strategies and return paths + metrics + annual returns."""
    all_paths = []
    metrics_rows = []
    annual_return_rows = []

    for name, weights in strategies.items():
        path_df, annual_returns = run_backtest(returns_df, weights, initial_value, rebalance_mode)
        metrics = calculate_metrics(path_df, annual_returns, risk_free_rate)
        metrics["strategy"] = name

        p = path_df.copy()
        p["strategy"] = name
        all_paths.append(p)
        metrics_rows.append(metrics)

        annual_df = pd.DataFrame(
            {
                "year": returns_df.sort_values("year")["year"].values,
                "annual_return": annual_returns.values,
                "strategy": name,
            }
        )
        annual_return_rows.append(annual_df)

    return (
        pd.concat(all_paths, ignore_index=True),
        pd.DataFrame(metrics_rows),
        pd.concat(annual_return_rows, ignore_index=True),
    )
