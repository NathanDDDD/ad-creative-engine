"""
Mock market data for testing when external APIs are unavailable.
"""
import random
from datetime import datetime, timedelta
from typing import List


def generate_mock_candles(symbol: str, timeframe: str, limit: int = 200) -> List[List[float]]:
    """
    Generate mock OHLCV candles for testing.
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe
        limit: Number of candles
        
    Returns:
        List of [timestamp, open, high, low, close, volume] candles
    """
    # Base prices for different symbols
    base_prices = {
        'BTC/USDT:USDT': 42000,
        'ETH/USDT:USDT': 2200,
        'SOL/USDT:USDT': 95,
    }
    
    base_price = base_prices.get(symbol, 1000)
    candles = []
    
    # Generate candles with realistic-looking data
    current_time = datetime.now()
    interval_minutes = 15
    
    price = base_price
    
    for i in range(limit):
        timestamp = current_time - timedelta(minutes=(limit - i) * interval_minutes)
        timestamp_ms = int(timestamp.timestamp() * 1000)
        
        # Simulate price movement
        change_pct = random.uniform(-0.01, 0.01)  # -1% to +1%
        price = price * (1 + change_pct)
        
        open_price = price
        high = price * (1 + abs(random.uniform(0, 0.005)))
        low = price * (1 - abs(random.uniform(0, 0.005)))
        close = random.uniform(low, high)
        volume = random.uniform(1000000, 5000000)
        
        candles.append([timestamp_ms, open_price, high, low, close, volume])
        price = close
    
    return candles


def get_mock_current_price(symbol: str) -> float:
    """Get mock current price for a symbol."""
    base_prices = {
        'BTC/USDT:USDT': 42345.67,
        'ETH/USDT:USDT': 2234.56,
        'SOL/USDT:USDT': 96.78,
    }
    return base_prices.get(symbol, 1000.0)
