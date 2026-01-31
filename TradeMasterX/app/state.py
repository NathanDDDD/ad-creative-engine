"""
State schema for TradeMasterX LangGraph workflow.
Pure rule-based decisions - NO LLM dependency.
"""
from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class TradingState(TypedDict, total=False):
    """State passed between nodes in the LangGraph workflow."""
    
    # Input
    symbol: str
    timeframe: str
    timestamp: str
    
    # Market data (from Bybit public API via ccxt)
    candles: List[List[float]]  # [timestamp, open, high, low, close, volume]
    current_price: float
    
    # Indicators (calculated from candles)
    ema_50: float
    ema_200: float
    rsi: float
    atr: float
    volume_change_pct: float
    
    # Pattern analysis
    trend: str  # "uptrend", "downtrend", "sideways"
    support: float
    resistance: float
    breakout_detected: bool
    breakout_type: str  # "upward", "downward", "none"
    
    # Signal fusion (rule-based)
    direction: str  # "LONG", "SHORT", "SKIP"
    confidence: int  # 0-100
    reasons: List[str]
    
    # Risk management
    entry: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    position_size_usdt: Optional[float]
    leverage_suggestion: Optional[int]
    invalidation: str
    risk_reward_ratio: Optional[float]
    
    # Paper trading
    paper_balance: float
    open_position: Optional[Dict[str, Any]]
    
    # Output
    notes: str
    error: Optional[str]


class Position(TypedDict):
    """Open position details for paper trading."""
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    entry_time: str
    stop_loss: float
    take_profit: float
    position_size_usdt: float
    leverage: int
    unrealized_pnl: float
    unrealized_pnl_pct: float
