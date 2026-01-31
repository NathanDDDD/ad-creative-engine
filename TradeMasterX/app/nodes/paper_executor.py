"""
Paper Executor Node - Simulates position management.
Tracks open positions and calculates unrealized PnL.
"""
from typing import Dict, Any
from ..utils.storage import Storage
from ..config import Config


def paper_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute paper trades and manage positions.
    
    Args:
        state: Current trading state with decision
        
    Returns:
        Updated state with position info
    """
    print(f"[Paper Executor] Managing simulated positions")
    
    symbol = state['symbol']
    direction = state.get('direction', 'SKIP')
    current_price = state.get('current_price')
    
    try:
        storage = Storage(Config.DB_PATH)
        
        # Check for existing open position
        open_position = storage.get_open_position(symbol)
        
        if open_position:
            # Update unrealized PnL for existing position
            entry_price = open_position['entry_price']
            stop_loss = open_position['stop_loss']
            take_profit = open_position['take_profit']
            side = open_position['side']
            position_size = open_position['position_size_usdt']
            leverage = open_position['leverage']
            
            # Calculate unrealized PnL
            if side == 'LONG':
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:  # SHORT
                pnl_pct = ((entry_price - current_price) / entry_price) * 100
            
            unrealized_pnl = (pnl_pct / 100) * position_size * leverage
            
            # Check if SL or TP hit
            close_position = False
            close_reason = None
            
            if side == 'LONG':
                if current_price <= stop_loss:
                    close_position = True
                    close_reason = "Stop Loss Hit"
                elif current_price >= take_profit:
                    close_position = True
                    close_reason = "Take Profit Hit"
            else:  # SHORT
                if current_price >= stop_loss:
                    close_position = True
                    close_reason = "Stop Loss Hit"
                elif current_price <= take_profit:
                    close_position = True
                    close_reason = "Take Profit Hit"
            
            # Close position if triggered
            if close_position:
                storage.close_trade(open_position['id'], current_price, close_reason)
                print(f"[Paper Executor] ✓ Position CLOSED: {close_reason}")
                print(f"[Paper Executor]   PnL: ${unrealized_pnl:+,.2f} ({pnl_pct:+.2f}%)")
                state['open_position'] = None
                state['notes'] = f"Closed {side} position: {close_reason}"
            else:
                # Update state with open position info
                state['open_position'] = {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': entry_price,
                    'entry_time': open_position['entry_time'],
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'position_size_usdt': position_size,
                    'leverage': leverage,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': pnl_pct
                }
                print(f"[Paper Executor] ✓ Open {side} position")
                print(f"[Paper Executor]   Unrealized PnL: ${unrealized_pnl:+,.2f} ({pnl_pct:+.2f}%)")
                
                # Don't open new position if one is already open
                state['direction'] = 'SKIP'
                state['reasons'] = [f"Already in {side} position"]
        
        else:
            # No open position
            state['open_position'] = None
            
            # Open new position if signal is valid
            if direction in ['LONG', 'SHORT'] and not state.get('error'):
                new_position = {
                    'symbol': symbol,
                    'side': direction,
                    'entry_time': state.get('timestamp'),
                    'entry_price': state.get('entry'),
                    'stop_loss': state.get('stop_loss'),
                    'take_profit': state.get('take_profit'),
                    'position_size_usdt': state.get('position_size_usdt'),
                    'leverage': state.get('leverage_suggestion'),
                }
                
                trade_id = storage.open_trade(new_position)
                
                print(f"[Paper Executor] ✓ Opened {direction} position (ID: {trade_id})")
                print(f"[Paper Executor]   Entry: ${new_position['entry_price']:,.2f}")
                print(f"[Paper Executor]   Size: ${new_position['position_size_usdt']:,.2f}")
                
                state['open_position'] = {
                    **new_position,
                    'unrealized_pnl': 0.0,
                    'unrealized_pnl_pct': 0.0
                }
                state['notes'] = f"Opened {direction} position"
            else:
                print(f"[Paper Executor] ✓ No new position (decision: {direction})")
        
        storage.close()
        
    except Exception as e:
        print(f"[Paper Executor] ✗ ERROR: {str(e)}")
        state['error'] = f"Paper execution error: {str(e)}"
        state['open_position'] = None
    
    return state
