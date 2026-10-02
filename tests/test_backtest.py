import pandas as pd

from calculators.backtest import compare_strategies, run_backtest, validate_weights
from data.sample_returns import SAMPLE_RETURNS


def test_validate_weights_detects_invalid_total():
    ok, msg = validate_weights({"us_equity": 50, "intl_equity": 40, "us_bonds": 0, "reit": 0, "cash": 0})
    assert not ok
    assert "100" in msg


def test_run_backtest_returns_expected_shape():
    df = pd.DataFrame(SAMPLE_RETURNS)
    path, annual_returns = run_backtest(
        df,
        {"us_equity": 60, "intl_equity": 20, "us_bonds": 15, "reit": 5, "cash": 0},
        initial_value=100000,
        rebalance_mode="annual",
    )

    assert len(path) == len(df) + 1
    assert len(annual_returns) == len(df)
    assert path["portfolio_value"].iloc[0] == 100000


def test_compare_strategies_outputs_multiple_tables():
    df = pd.DataFrame(SAMPLE_RETURNS)
    strategies = {
        "Core": {"us_equity": 45, "intl_equity": 15, "us_bonds": 35, "reit": 5, "cash": 0},
        "Defensive": {"us_equity": 30, "intl_equity": 10, "us_bonds": 50, "reit": 5, "cash": 5},
    }

    paths_df, metrics_df, annual_df = compare_strategies(df, strategies, initial_value=250000)

    assert set(metrics_df["strategy"]) == {"Core", "Defensive"}
    assert len(paths_df["strategy"].unique()) == 2
    assert len(annual_df["strategy"].unique()) == 2
