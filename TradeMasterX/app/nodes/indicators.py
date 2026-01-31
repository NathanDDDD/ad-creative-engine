"""
Indicators Node - Calculates technical indicators.
Pure calculation - no external dependencies.
"""
import pandas as pd
from typing import Dict, Any
from ..utils.ta import calculate_ema, calculate_rsi, calculate_atr, calculate_volume_change


def indicators_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate technical indicators from candles.
    
    Args:
        state: Current trading state with candles
        
    Returns:
        Updated state with calculated indicators
    """
    print(f"[Indicators] Calculating EMA50/200, RSI14, ATR14")
    
    # Skip if error already occurred
    if state.get('error'):
        return state
    
    try:
        candles = state.get('candles', [])
        if not candles:
            raise ValueError("No candles available")
        
        # Convert to DataFrame
        df = pd.DataFrame(
            candles, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        from ..config import Config
        
        # Calculate indicators
        state['ema_50'] = calculate_ema(df['close'], Config.EMA_FAST)
        state['ema_200'] = calculate_ema(df['close'], Config.EMA_SLOW)
        state['rsi'] = calculate_rsi(df['close'], Config.RSI_PERIOD)
        state['atr'] = calculate_atr(df['high'], df['low'], df['close'], Config.ATR_PERIOD)
        state['volume_change_pct'] = calculate_volume_change(df['volume'])
        
        print(f"[Indicators] ✓ EMA50: ${state['ema_50']:,.2f}, EMA200: ${state['ema_200']:,.2f}")
        print(f"[Indicators] ✓ RSI: {state['rsi']:.1f}, ATR: ${state['atr']:,.2f}")
        print(f"[Indicators] ✓ Volume Change: {state['volume_change_pct']:+.1f}%")
        
    except Exception as e:
        print(f"[Indicators] ✗ ERROR: {str(e)}")
        state['error'] = f"Indicator calculation error: {str(e)}"
        state['direction'] = 'SKIP'
        state['confidence'] = 0
        state['reasons'] = ['Indicator calculation failed']
    
    return state
