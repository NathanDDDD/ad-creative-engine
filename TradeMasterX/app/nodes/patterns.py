"""
Patterns Node - Detects market patterns.
Simple heuristic-based detection - no LLM required.
"""
from typing import Dict, Any
from ..utils.ta import detect_support_resistance, detect_trend, detect_breakout


def patterns_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect market patterns using simple heuristics.
    
    Args:
        state: Current trading state with indicators
        
    Returns:
        Updated state with pattern analysis
    """
    print(f"[Patterns] Analyzing market structure")
    
    # Skip if error already occurred
    if state.get('error'):
        return state
    
    try:
        candles = state.get('candles', [])
        current_price = state.get('current_price')
        ema_50 = state.get('ema_50')
        ema_200 = state.get('ema_200')
        
        if not candles or current_price is None:
            raise ValueError("Missing required data")
        
        # Detect support and resistance
        support, resistance = detect_support_resistance(candles, lookback=20)
        
        # Detect trend
        trend = detect_trend(ema_50, ema_200, current_price)
        
        # Detect breakout
        breakout_detected, breakout_type = detect_breakout(
            current_price, support, resistance, threshold=0.005
        )
        
        # Update state
        state['support'] = support
        state['resistance'] = resistance
        state['trend'] = trend
        state['breakout_detected'] = breakout_detected
        state['breakout_type'] = breakout_type
        
        print(f"[Patterns] ✓ Trend: {trend.upper()}")
        print(f"[Patterns] ✓ Support: ${support:,.2f}, Resistance: ${resistance:,.2f}")
        if breakout_detected:
            print(f"[Patterns] ✓ Breakout: {breakout_type.upper()}")
        
    except Exception as e:
        print(f"[Patterns] ✗ ERROR: {str(e)}")
        state['error'] = f"Pattern analysis error: {str(e)}"
        state['direction'] = 'SKIP'
        state['confidence'] = 0
        state['reasons'] = ['Pattern analysis failed']
    
    return state
