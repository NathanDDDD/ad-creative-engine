# ad-creative-engine

## TradeMasterX - Bybit Futures Paper Trading Bot

A rule-based paper trading bot for Bybit USDT perpetual futures.

See [TradeMasterX/README.md](TradeMasterX/README.md) for complete documentation.

### Quick Start

```bash
cd TradeMasterX
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app/run_bot.py --once
```

### Features

- 🎯 Paper trading only (no real orders)
- 🔓 Uses only FREE public APIs (no API keys needed)
- 🤖 Rule-based decisions (no LLM dependency)
- 📊 15-minute timeframe analysis
- 💾 SQLite journaling
- 📈 Tracks performance metrics
- 🔍 Optional LangSmith tracing