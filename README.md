# Rates & FX Pricing, Curves & Risk Analytics

Python research project: annual par-swap discount-curve bootstrapping, bond pricing and DV01, receive-fixed swaps, EUR/USD covered-interest-parity forwards and stress scenarios.

All examples are educational, not executable trading signals. Synthetic demo data are clearly identified; optional public ECB/FRED series are used for reference, not represented as swap/OIS curves.

## Quick start

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python examples/run_demo.py
streamlit run app.py
```

**Limitations:** single-curve assumptions; no CSA/multi-curve or basis, no bid/ask, calendar conventions, CVA, funding or liquidity modeling. No investment advice.
