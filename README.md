# Asset Allocation Backtester

Advisor-focused Streamlit tool to compare allocation strategies under annual rebalance versus buy-and-hold behavior.

## Features
- Multi-strategy allocation comparison
- Allocation validation (must total 100% per strategy)
- Rebalance mode toggle: annual or buy-and-hold
- Portfolio growth and annual return visualizations
- Metrics: total return, CAGR, volatility, Sharpe, Calmar, max drawdown, best/worst year, positive-year ratio

## Setup
```bash
git clone https://github.com/john-stromberg/asset-allocation-backtester.git
cd asset-allocation-backtester
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Default local app URL: `http://localhost:8502`

## Test
```bash
python -m pytest tests/test_backtest.py
```

## Project Structure
- `app.py` - Streamlit UI
- `calculators/backtest.py` - backtest and risk metric logic
- `data/sample_returns.py` - sample annual return inputs
- `tests/test_backtest.py` - unit tests for core engine

## Notes
Uses embedded sample annual return data for prototyping and advisor workflow demos.
