"""
Market Data Node - Fetches public market data from Bybit.
Uses ccxt with NO API keys (public data only).
"""
import ccxt
from datetime import datetime
from typing import Dict, Any


def market_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch latest market data from Bybit public API.
    NO API KEYS REQUIRED - uses public endpoints only.
    
    Args:
        state: Current trading state
        
    Returns:
        Updated state with market data or error
    """
    symbol = state['symbol']
    timeframe = state['timeframe']
    
    print(f"\n[Market Data] Fetching {symbol} @ {timeframe}")
    
    try:
        # Initialize Bybit exchange with NO API keys (public data only)
        exchange = ccxt.bybit({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'linear',  # USDT perpetuals
            }
        })
        
        # Fetch OHLCV candles (public endpoint)
        from ..config import Config
        candles = exchange.fetch_ohlcv(
            symbol, 
            timeframe, 
            limit=Config.LOOKBACK_PERIODS
        )
        
        if not candles or len(candles) < 50:
            raise ValueError(f"Insufficient candles: {len(candles) if candles else 0}")
        
        # Fetch current ticker (public endpoint)
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker.get('last') or candles[-1][4]
        
        # Update state
        state['candles'] = candles
        state['current_price'] = current_price
        state['timestamp'] = datetime.now().isoformat()
        
        print(f"[Market Data] ✓ Fetched {len(candles)} candles, price: ${current_price:,.2f}")
        
    except Exception as e:
        print(f"[Market Data] ✗ ERROR: {str(e)}")
        state['error'] = f"Market data error: {str(e)}"
        state['direction'] = 'SKIP'
        state['confidence'] = 0
        state['reasons'] = ['Market data unavailable']
        state['notes'] = f"Failed to fetch data: {str(e)}"
    
    return state
