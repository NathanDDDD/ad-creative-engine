"""
Fusion Node - Combines signals into trading decision.
Pure rule-based logic - NO LLM dependency.
"""
from typing import Dict, Any, List, Tuple
import numpy as np


def analyze_long_signals(state: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Analyze conditions for LONG entry.
    Rule-based scoring system.
    
    Returns:
        (confidence_score, reasons)
    """
    confidence = 0
    reasons = []
    
    trend = state.get('trend', 'sideways')
    rsi = state.get('rsi', 50)
    ema_50 = state.get('ema_50', 0)
    ema_200 = state.get('ema_200', 0)
    current_price = state.get('current_price', 0)
    volume_change = state.get('volume_change_pct', 0)
    breakout_detected = state.get('breakout_detected', False)
    breakout_type = state.get('breakout_type', 'none')
    
    # Trend alignment (30 points max)
    if trend == "uptrend":
        confidence += 30
        reasons.append(f"Strong uptrend (price > EMA50 > EMA200)")
    elif trend == "sideways" and current_price > ema_50:
        confidence += 10
        reasons.append(f"Price above EMA50")
    
    # RSI conditions (20 points max)
    if not np.isnan(rsi):
        if 40 <= rsi <= 70:
            confidence += 20
            reasons.append(f"RSI optimal for long ({rsi:.1f})")
        elif 30 <= rsi < 40:
            confidence += 15
            reasons.append(f"RSI oversold - reversal potential ({rsi:.1f})")
        elif rsi < 30:
            confidence += 10
            reasons.append(f"RSI deeply oversold ({rsi:.1f})")
    
    # Price position (15 points max)
    if not np.isnan(ema_50) and not np.isnan(ema_200):
        if current_price > ema_50 and current_price > ema_200:
            confidence += 15
            reasons.append("Price above both EMAs")
        elif current_price > ema_50:
            confidence += 8
            reasons.append("Price above EMA50")
    
    # Volume (15 points max)
    if volume_change > 50:
        confidence += 15
        reasons.append(f"Very high volume (+{volume_change:.1f}%)")
    elif volume_change > 20:
        confidence += 10
        reasons.append(f"High volume (+{volume_change:.1f}%)")
    elif volume_change > 0:
        confidence += 5
        reasons.append(f"Volume increase (+{volume_change:.1f}%)")
    
    # Breakout (20 points max)
    if breakout_detected and breakout_type == "upward":
        confidence += 20
        reasons.append("Upward breakout detected")
    
    return confidence, reasons


def analyze_short_signals(state: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Analyze conditions for SHORT entry.
    Rule-based scoring system.
    
    Returns:
        (confidence_score, reasons)
    """
    confidence = 0
    reasons = []
    
    trend = state.get('trend', 'sideways')
    rsi = state.get('rsi', 50)
    ema_50 = state.get('ema_50', 0)
    ema_200 = state.get('ema_200', 0)
    current_price = state.get('current_price', 0)
    volume_change = state.get('volume_change_pct', 0)
    breakout_detected = state.get('breakout_detected', False)
    breakout_type = state.get('breakout_type', 'none')
    
    # Trend alignment (30 points max)
    if trend == "downtrend":
        confidence += 30
        reasons.append(f"Strong downtrend (price < EMA50 < EMA200)")
    elif trend == "sideways" and current_price < ema_50:
        confidence += 10
        reasons.append(f"Price below EMA50")
    
    # RSI conditions (20 points max)
    if not np.isnan(rsi):
        if 30 <= rsi <= 60:
            confidence += 20
            reasons.append(f"RSI optimal for short ({rsi:.1f})")
        elif 60 < rsi <= 70:
            confidence += 15
            reasons.append(f"RSI overbought - reversal potential ({rsi:.1f})")
        elif rsi > 70:
            confidence += 10
            reasons.append(f"RSI deeply overbought ({rsi:.1f})")
    
    # Price position (15 points max)
    if not np.isnan(ema_50) and not np.isnan(ema_200):
        if current_price < ema_50 and current_price < ema_200:
            confidence += 15
            reasons.append("Price below both EMAs")
        elif current_price < ema_50:
            confidence += 8
            reasons.append("Price below EMA50")
    
    # Volume (15 points max)
    if volume_change > 50:
        confidence += 15
        reasons.append(f"Very high volume (+{volume_change:.1f}%)")
    elif volume_change > 20:
        confidence += 10
        reasons.append(f"High volume (+{volume_change:.1f}%)")
    elif volume_change > 0:
        confidence += 5
        reasons.append(f"Volume increase (+{volume_change:.1f}%)")
    
    # Breakout (20 points max)
    if breakout_detected and breakout_type == "downward":
        confidence += 20
        reasons.append("Downward breakout detected")
    
    return confidence, reasons


def fusion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine all signals into final trading decision.
    RULE-BASED ONLY - no LLM calls.
    
    Args:
        state: Current trading state
        
    Returns:
        Updated state with decision
    """
    print(f"[Fusion] Combining signals into decision")
    
    # Skip if error already occurred
    if state.get('error'):
        return state
    
    try:
        # Analyze both directions
        long_conf, long_reasons = analyze_long_signals(state)
        short_conf, short_reasons = analyze_short_signals(state)
        
        from ..config import Config
        
        # Determine direction based on highest confidence
        if long_conf > short_conf and long_conf >= Config.MIN_CONFIDENCE:
            direction = "LONG"
            confidence = long_conf
            reasons = long_reasons
        elif short_conf > long_conf and short_conf >= Config.MIN_CONFIDENCE:
            direction = "SHORT"
            confidence = short_conf
            reasons = short_reasons
        else:
            direction = "SKIP"
            confidence = max(long_conf, short_conf)
            reasons = [
                f"Insufficient confidence (Long: {long_conf}, Short: {short_conf})",
                f"Minimum required: {Config.MIN_CONFIDENCE}"
            ]
        
        # Update state
        state['direction'] = direction
        state['confidence'] = confidence
        state['reasons'] = reasons
        
        print(f"[Fusion] ✓ Decision: {direction} (confidence: {confidence}%)")
        for reason in reasons[:3]:  # Show top 3 reasons
            print(f"[Fusion]   • {reason}")
        
    except Exception as e:
        print(f"[Fusion] ✗ ERROR: {str(e)}")
        state['error'] = f"Signal fusion error: {str(e)}"
        state['direction'] = 'SKIP'
        state['confidence'] = 0
        state['reasons'] = ['Signal fusion failed']
    
    return state
