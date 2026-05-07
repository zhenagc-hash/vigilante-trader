# vigilante-trader

Trade insight system with 100 AI-style market agents.

## Bitcoin market chart analysis system

This repository now includes a minimal Python pipeline that:

1. Fetches Bitcoin market chart data from CoinGecko
2. Runs analysis with 100 independent agents
3. Produces a consensus trend report

### Run

```bash
python vigilante_trader.py
```

### Test

```bash
python -m unittest tests/test_vigilante_trader.py -v
```
