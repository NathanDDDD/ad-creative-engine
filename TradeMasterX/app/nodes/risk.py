"""
Risk Management Node - Calculates position sizing and risk parameters.
Pure calculation - no external dependencies.
"""
from typing import Dict, Any
import numpy as np


def risk_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate entry, stop loss, take profit, and position sizing.
    Enforces risk management rules.
    
    Args:
        state: Current trading state with decision
        
    Returns:
        Updated state with risk parameters
    """
    print(f"[Risk] Calculating position sizing and risk levels")
    
    # Skip if error or SKIP decision
    if state.get('error') or state.get('direction') == 'SKIP':
        state['entry'] = None
        state['stop_loss'] = None
        state['take_profit'] = None
        state['position_size_usdt'] = None
        state['leverage_suggestion'] = None
        state['invalidation'] = "No trade taken"
        state['risk_reward_ratio'] = None
        return state
    
    try:
        from ..config import Config
        
        direction = state['direction']
        current_price = state['current_price']
        atr = state.get('atr', 0)
        support = state.get('support', current_price * 0.95)
        resistance = state.get('resistance', current_price * 1.05)
        paper_balance = state.get('paper_balance', Config.INITIAL_BALANCE)
        
        # Entry price (current market price)
        entry = current_price
        
        # Calculate stop loss using ATR
        atr_multiplier = 2.0  # 2x ATR for stop loss
        
        if direction == "LONG":
            # For LONG: SL below entry, TP above entry
            stop_loss = entry - (atr * atr_multiplier)
            # Use support as a reference, take the higher SL
            if support > stop_loss:
                stop_loss = support * 0.995  # Just below support
            
            # Calculate TP using preferred RR
            risk_amount = entry - stop_loss
            take_profit = entry + (risk_amount * Config.PREFERRED_RISK_REWARD)
            
            invalidation = f"Price below ${stop_loss:,.2f}"
            
        else:  # SHORT
            # For SHORT: SL above entry, TP below entry
            stop_loss = entry + (atr * atr_multiplier)
            # Use resistance as a reference, take the lower SL
            if resistance < stop_loss:
                stop_loss = resistance * 1.005  # Just above resistance
            
            # Calculate TP using preferred RR
            risk_amount = stop_loss - entry
            take_profit = entry - (risk_amount * Config.PREFERRED_RISK_REWARD)
            
            invalidation = f"Price above ${stop_loss:,.2f}"
        
        # Calculate risk/reward ratio
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Validate minimum RR
        if risk_reward_ratio < Config.MIN_RISK_REWARD:
            print(f"[Risk] ✗ Risk/Reward too low: {risk_reward_ratio:.2f} < {Config.MIN_RISK_REWARD}")
            state['direction'] = 'SKIP'
            state['reasons'].append(f"Risk/Reward too low ({risk_reward_ratio:.2f})")
            state['entry'] = None
            state['stop_loss'] = None
            state['take_profit'] = None
            state['position_size_usdt'] = None
            state['leverage_suggestion'] = None
            state['invalidation'] = "Risk/Reward ratio insufficient"
            state['risk_reward_ratio'] = risk_reward_ratio
            return state
        
        # Calculate position size (risk 1% of balance)
        risk_per_trade = paper_balance * Config.MAX_RISK_PER_TRADE
        risk_pct_per_unit = (risk / entry) * 100
        
        # Position size in USDT
        position_size_usdt = (risk_per_trade / risk_pct_per_unit) * 100
        
        # Limit position size to reasonable amount
        max_position = paper_balance * 0.5  # Max 50% of balance per trade
        if position_size_usdt > max_position:
            position_size_usdt = max_position
        
        # Suggest leverage (keep it low for safety)
        leverage_suggestion = min(3, Config.MAX_LEVERAGE)  # Default 3x, max from config
        
        # Update state
        state['entry'] = entry
        state['stop_loss'] = stop_loss
        state['take_profit'] = take_profit
        state['position_size_usdt'] = position_size_usdt
        state['leverage_suggestion'] = leverage_suggestion
        state['invalidation'] = invalidation
        state['risk_reward_ratio'] = risk_reward_ratio
        
        print(f"[Risk] ✓ Entry: ${entry:,.2f}")
        print(f"[Risk] ✓ Stop Loss: ${stop_loss:,.2f} ({direction})")
        print(f"[Risk] ✓ Take Profit: ${take_profit:,.2f}")
        print(f"[Risk] ✓ Risk/Reward: {risk_reward_ratio:.2f}")
        print(f"[Risk] ✓ Position Size: ${position_size_usdt:,.2f}")
        print(f"[Risk] ✓ Leverage: {leverage_suggestion}x")
        
    except Exception as e:
        print(f"[Risk] ✗ ERROR: {str(e)}")
        state['error'] = f"Risk calculation error: {str(e)}"
        state['direction'] = 'SKIP'
        state['reasons'].append('Risk calculation failed')
        state['entry'] = None
        state['stop_loss'] = None
        state['take_profit'] = None
        state['position_size_usdt'] = None
        state['leverage_suggestion'] = None
        state['invalidation'] = "Risk calculation error"
    
    return state
