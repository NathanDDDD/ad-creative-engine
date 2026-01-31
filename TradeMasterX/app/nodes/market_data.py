"""
Market Data Node - Fetches public market data from Bybit.
Uses ccxt with NO API keys (public data only).
Fallback to mock data if API unavailable (for testing).
"""
import ccxt
from datetime import datetime
from typing import Dict, Any


def market_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch latest market data from Bybit public API.
    NO API KEYS REQUIRED - uses public endpoints only.
    Falls back to mock data if API unavailable (demo mode).
    
    Args:
        state: Current trading state
        
    Returns:
        Updated state with market data or error
    """
    symbol = state['symbol']
    timeframe = state['timeframe']
    
    print(f"\n[Market Data] Fetching {symbol} @ {timeframe}")
    
    from ..config import Config
    
    # Try real API first
    try:
        # Initialize Bybit exchange with NO API keys (public data only)
        exchange = ccxt.bybit({
            'enableRateLimit': True,
        })
        
        # Load markets first
        exchange.load_markets()
        
        # Fetch OHLCV candles (public endpoint)
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
        # Fall back to mock data for testing
        print(f"[Market Data] ⚠ API unavailable: {str(e)}")
        print(f"[Market Data] ⚠ Using DEMO MODE with mock data")
        
        try:
            from ..utils.mock_data import generate_mock_candles, get_mock_current_price
            
            candles = generate_mock_candles(symbol, timeframe, Config.LOOKBACK_PERIODS)
            current_price = get_mock_current_price(symbol)
            
            state['candles'] = candles
            state['current_price'] = current_price
            state['timestamp'] = datetime.now().isoformat()
            state['notes'] = "DEMO MODE: Using mock data (API unavailable)"
            
            print(f"[Market Data] ✓ Generated {len(candles)} mock candles, price: ${current_price:,.2f}")
            
        except Exception as mock_error:
            print(f"[Market Data] ✗ ERROR: Mock data also failed: {str(mock_error)}")
            state['error'] = f"Market data error: {str(e)}"
            state['direction'] = 'SKIP'
            state['confidence'] = 0
            state['reasons'] = ['Market data unavailable']
            state['notes'] = f"Failed to fetch data: {str(e)}"
    
    return state
