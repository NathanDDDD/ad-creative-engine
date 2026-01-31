"""
Technical analysis utilities.
Pure calculation - no external API dependencies.
"""
import pandas as pd
import numpy as np
from typing import List, Tuple


def calculate_ema(data: pd.Series, period: int) -> float:
    """Calculate Exponential Moving Average for the most recent value."""
    if len(data) < period:
        return float('nan')
    return data.ewm(span=period, adjust=False).mean().iloc[-1]


def calculate_rsi(data: pd.Series, period: int = 14) -> float:
    """Calculate RSI for the most recent value."""
    if len(data) < period + 1:
        return 50.0  # Neutral default
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    """Calculate Average True Range for the most recent value."""
    if len(high) < period + 1:
        return 0.0
    
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(period).mean()
    return atr.iloc[-1]


def calculate_volume_change(volume: pd.Series, lookback: int = 20) -> float:
    """
    Calculate volume change percentage compared to average.
    
    Returns:
        Percentage change from average volume
    """
    if len(volume) < lookback + 1:
        return 0.0
    
    avg_volume = volume.iloc[-lookback:-1].mean()
    current_volume = volume.iloc[-1]
    
    if avg_volume == 0:
        return 0.0
    
    return ((current_volume - avg_volume) / avg_volume) * 100


def detect_support_resistance(candles: List[List[float]], lookback: int = 20) -> Tuple[float, float]:
    """
    Detect support and resistance levels from recent candles.
    
    Args:
        candles: OHLCV candles [timestamp, open, high, low, close, volume]
        lookback: Number of recent candles to analyze
        
    Returns:
        Tuple of (support, resistance)
    """
    if len(candles) < lookback:
        lookback = len(candles)
    
    recent_candles = candles[-lookback:]
    
    # Support: lowest low in recent period
    support = min([candle[3] for candle in recent_candles])
    
    # Resistance: highest high in recent period
    resistance = max([candle[2] for candle in recent_candles])
    
    return support, resistance


def detect_trend(ema_50: float, ema_200: float, current_price: float) -> str:
    """
    Detect trend based on EMA alignment.
    
    Returns:
        "uptrend", "downtrend", or "sideways"
    """
    if np.isnan(ema_50) or np.isnan(ema_200):
        return "sideways"
    
    # Strong uptrend: price > EMA50 > EMA200
    if current_price > ema_50 > ema_200:
        return "uptrend"
    
    # Strong downtrend: price < EMA50 < EMA200
    if current_price < ema_50 < ema_200:
        return "downtrend"
    
    return "sideways"


def detect_breakout(current_price: float, support: float, resistance: float,
                    threshold: float = 0.005) -> Tuple[bool, str]:
    """
    Detect if price has broken out of recent range.
    
    Args:
        current_price: Current market price
        support: Support level
        resistance: Resistance level
        threshold: Breakout threshold (0.5% default)
        
    Returns:
        Tuple of (breakout_detected, breakout_type)
    """
    range_size = resistance - support
    breakout_buffer = range_size * threshold
    
    if current_price > resistance + breakout_buffer:
        return True, "upward"
    elif current_price < support - breakout_buffer:
        return True, "downward"
    
    return False, "none"
