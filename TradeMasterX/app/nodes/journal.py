"""
Journal Node - Logs all runs and trades to SQLite.
"""
from typing import Dict, Any
from ..utils.storage import Storage
from ..config import Config


def journal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log run to database.
    
    Args:
        state: Current trading state
        
    Returns:
        State with notes updated
    """
    print(f"[Journal] Logging run to database")
    
    try:
        storage = Storage(Config.DB_PATH)
        
        # Log this run
        storage.log_run(state)
        
        # Get performance summary
        perf = storage.get_performance_summary()
        
        print(f"[Journal] ✓ Run logged")
        print(f"[Journal] ✓ Performance: {perf.get('total_trades', 0)} trades, "
              f"{perf.get('win_rate', 0):.1f}% win rate")
        
        # Add performance note
        if not state.get('notes'):
            state['notes'] = ""
        
        state['notes'] += f" | Total trades: {perf.get('total_trades', 0)}, Win rate: {perf.get('win_rate', 0):.1f}%"
        
        storage.close()
        
    except Exception as e:
        print(f"[Journal] ✗ ERROR: {str(e)}")
        # Don't fail the whole workflow on journal error
        if not state.get('notes'):
            state['notes'] = ""
        state['notes'] += f" | Journal error: {str(e)}"
    
    return state
