# TradeMasterX - Bybit Futures Paper Trading Bot

A rule-based paper trading bot for Bybit USDT perpetual futures using LangGraph for workflow orchestration.

## Features

- **Market**: Bybit USDT Perpetual Futures
- **Timeframe**: 15 minutes (configurable)
- **Mode**: Paper trading only (no real orders)
- **Symbols**: BTC/USDT, ETH/USDT, SOL/USDT (configurable)
- **Decision Engine**: Rule-based (NO LLM dependency)
- **Data**: Public API only (NO API keys required)
- **Journaling**: SQLite database for trade logging
- **Tracing**: Optional LangSmith integration

## Tech Stack

- **LangGraph**: State machine workflow
- **LangChain**: Optional tracing (LangSmith)
- **ccxt**: Bybit public market data
- **pandas/numpy**: Technical indicators
- **SQLite**: Trade journal and performance tracking

## Architecture

### Workflow (LangGraph Nodes)

1. **Market Data**: Fetch last 200 candles via ccxt (public API, no keys needed)
2. **Indicators**: Calculate EMA50/200, RSI14, ATR14, volume change
3. **Patterns**: Detect breakouts, support/resistance, trend
4. **Fusion**: Combine signals → LONG/SHORT/SKIP decision (rule-based)
5. **Risk**: Calculate SL/TP using ATR, enforce RR ≥ 1.5
6. **Paper Executor**: Simulate positions, track unrealized PnL
7. **Journal**: Log every run to SQLite

### Decision Rules (No LLM)

The bot uses a **confidence scoring system** (0-100) based on:

- **Trend alignment** (30 pts): EMA positioning
- **RSI levels** (20 pts): Optimal zones for entry
- **Price position** (15 pts): Relative to EMAs
- **Volume confirmation** (15 pts): Above average volume
- **Breakout detection** (20 pts): Range breakouts

**Minimum confidence to trade**: 60%

If confidence < 60 for both directions → **SKIP**

## Installation

```bash
# Clone repository
cd TradeMasterX

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables (Optional)

```bash
# Copy example
cp .env.example .env

# Edit .env with your preferences
```

**.env.example**:
```env
# LangSmith Tracing (OPTIONAL - code runs without it)
LANGCHAIN_TRACING_V2=false
LANGSMITH_API_KEY=
LANGCHAIN_PROJECT=TradeMasterX

# Paper Trading Settings
INITIAL_BALANCE=10000.0
MAX_RISK_PER_TRADE=0.01
MIN_RISK_REWARD=1.5

# Trading Symbols (comma-separated)
SYMBOLS=BTC/USDT:USDT,ETH/USDT:USDT,SOL/USDT:USDT

# Timeframe
TIMEFRAME=15m

# Run interval in minutes (for loop mode)
RUN_INTERVAL_MINUTES=15
```

### LangSmith Tracing (Optional)

LangSmith tracing is **completely optional**. The bot works without it.

To enable:
1. Get free API key from https://smith.langchain.com/
2. Set in .env:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGSMITH_API_KEY=your_key_here
   ```

## Usage

### Single Run (Test)

Analyze all symbols once and exit:

```bash
python app/run_bot.py --once
```

### Loop Mode (Production)

Run continuously every 15 minutes:

```bash
python app/run_bot.py --loop
```

Press `Ctrl+C` to stop.

## Output Format

Each run outputs JSON with complete trade details:

```json
{
  "symbol": "BTC/USDT:USDT",
  "timeframe": "15m",
  "timestamp": "2024-01-31T12:34:56",
  "decision": "LONG",
  "confidence": 75,
  "entry": 42500.0,
  "stop_loss": 42000.0,
  "take_profit": 43500.0,
  "leverage_suggestion": 3,
  "position_size_usdt": 300.0,
  "reasons": [
    "Strong uptrend (price > EMA50 > EMA200)",
    "RSI optimal for long (58.3)",
    "High volume (+35.2%)"
  ],
  "invalidation": "Price below $42000.00",
  "notes": "Opened LONG position | Total trades: 5, Win rate: 60.0%",
  "open_position": {
    "side": "LONG",
    "entry_price": 42500.0,
    "stop_loss": 42000.0,
    "take_profit": 43500.0,
    "unrealized_pnl": 150.0,
    "unrealized_pnl_pct": 1.18
  },
  "current_price": 42600.0,
  "trend": "uptrend",
  "rsi": 58.3
}
```

## Database Schema

### Runs Table
Logs every execution (including SKIPs):
- timestamp, symbol, timeframe
- decision, confidence, reasons
- entry, stop_loss, take_profit
- current_price, trend, rsi, error

### Trades Table
Simulated positions:
- entry_time, entry_price
- stop_loss, take_profit
- position_size, leverage
- close_time, close_price, pnl
- status (OPEN/CLOSED)

### Performance Table
Performance snapshots:
- total_trades, win_rate
- total_pnl, avg_r
- avg_win_pct, avg_loss_pct

Query database:
```bash
sqlite3 journal.db "SELECT * FROM runs ORDER BY id DESC LIMIT 10;"
sqlite3 journal.db "SELECT * FROM trades WHERE status='CLOSED';"
```

## Risk Management

- **Max risk per trade**: 1% of paper balance
- **Minimum RR**: 1.5 (prefer 2.0)
- **Stop loss**: 2x ATR or support/resistance
- **Take profit**: RR ratio from stop loss
- **Leverage**: Default 3x (max 10x configurable)
- **Max position**: 50% of balance

## Safety Features

✅ **No real trading** - Paper only  
✅ **No API keys required** - Public data only  
✅ **Graceful error handling** - SKIPs on errors  
✅ **No LLM dependency** - Pure rule-based  
✅ **Optional tracing** - Works without LangSmith  
✅ **Rate limiting** - Built into ccxt  

## Example Output

```
================================================================================
TradeMasterX - Bybit Futures Paper Trading Bot
================================================================================
Mode: Single Run
Symbols: ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
Timeframe: 15m
Paper Balance: $10,000.00
================================================================================

================================================================================
Analyzing BTC/USDT:USDT
================================================================================

[Market Data] Fetching BTC/USDT:USDT @ 15m
[Market Data] ✓ Fetched 200 candles, price: $42,345.67

[Indicators] Calculating EMA50/200, RSI14, ATR14
[Indicators] ✓ EMA50: $41,234.56, EMA200: $40,123.45
[Indicators] ✓ RSI: 62.3, ATR: $234.56
[Indicators] ✓ Volume Change: +28.5%

[Patterns] Analyzing market structure
[Patterns] ✓ Trend: UPTREND
[Patterns] ✓ Support: $41,500.00, Resistance: $42,800.00

[Fusion] Combining signals into decision
[Fusion] ✓ Decision: LONG (confidence: 75%)
[Fusion]   • Strong uptrend (price > EMA50 > EMA200)
[Fusion]   • RSI optimal for long (62.3)
[Fusion]   • High volume (+28.5%)

[Risk] Calculating position sizing and risk levels
[Risk] ✓ Entry: $42,345.67
[Risk] ✓ Stop Loss: $41,876.55 (LONG)
[Risk] ✓ Take Profit: $43,283.91
[Risk] ✓ Risk/Reward: 2.00
[Risk] ✓ Position Size: $213.58
[Risk] ✓ Leverage: 3x

[Paper Executor] Managing simulated positions
[Paper Executor] ✓ Opened LONG position (ID: 1)
[Paper Executor]   Entry: $42,345.67
[Paper Executor]   Size: $213.58

[Journal] Logging run to database
[Journal] ✓ Run logged
[Journal] ✓ Performance: 1 trades, 0.0% win rate

================================================================================
RESULT
================================================================================
{
  "symbol": "BTC/USDT:USDT",
  "timeframe": "15m",
  "timestamp": "2024-01-31T12:34:56.789012",
  "decision": "LONG",
  "confidence": 75,
  ...
}
```

## Troubleshooting

### Issue: "Market data unavailable"
- **Cause**: Network error or Bybit API down
- **Solution**: Check internet connection, wait and retry

### Issue: "Insufficient candles"
- **Cause**: Symbol not available or new listing
- **Solution**: Check symbol format (e.g., "BTC/USDT:USDT" for futures)

### Issue: "LangSmith tracing failed"
- **Cause**: Invalid API key or network issue
- **Solution**: Tracing is optional, bot continues without it

## License

MIT

## Disclaimer

**This is a paper trading bot for educational purposes only.**

- NO real trading occurs
- NO financial advice provided
- Use at your own risk
- Past performance does not guarantee future results

---

Built with ❤️ using LangGraph
