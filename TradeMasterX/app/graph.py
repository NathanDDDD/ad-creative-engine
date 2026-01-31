"""
LangGraph workflow for TradeMasterX trading bot.
Connects all nodes into a state machine with optional LangSmith tracing.
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import os

from .state import TradingState
from .config import Config
from .nodes.market_data import market_data_node
from .nodes.indicators import indicators_node
from .nodes.patterns import patterns_node
from .nodes.fusion import fusion_node
from .nodes.risk import risk_node
from .nodes.paper_executor import paper_executor_node
from .nodes.journal import journal_node


def create_trading_graph():
    """
    Create the trading workflow graph.
    
    Workflow:
    1. Market Data -> fetch candles and current price
    2. Indicators -> calculate EMA, RSI, ATR, volume
    3. Patterns -> detect trend, support/resistance, breakouts
    4. Fusion -> combine signals into decision
    5. Risk -> calculate position sizing and risk levels
    6. Paper Executor -> manage simulated positions
    7. Journal -> log to database
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(TradingState)
    
    # Add nodes
    workflow.add_node("market_data", market_data_node)
    workflow.add_node("indicators", indicators_node)
    workflow.add_node("patterns", patterns_node)
    workflow.add_node("fusion", fusion_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("paper_executor", paper_executor_node)
    workflow.add_node("journal", journal_node)
    
    # Define edges (workflow sequence)
    workflow.set_entry_point("market_data")
    workflow.add_edge("market_data", "indicators")
    workflow.add_edge("indicators", "patterns")
    workflow.add_edge("patterns", "fusion")
    workflow.add_edge("fusion", "risk")
    workflow.add_edge("risk", "paper_executor")
    workflow.add_edge("paper_executor", "journal")
    workflow.add_edge("journal", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def setup_langsmith_tracing():
    """
    Setup LangSmith tracing if enabled.
    OPTIONAL - code works without it.
    """
    if Config.LANGCHAIN_TRACING_V2 and Config.LANGSMITH_API_KEY:
        try:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGSMITH_API_KEY"] = Config.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = Config.LANGCHAIN_PROJECT
            print(f"[LangSmith] ✓ Tracing enabled (project: {Config.LANGCHAIN_PROJECT})")
            return True
        except Exception as e:
            print(f"[LangSmith] ✗ Tracing setup failed: {e}")
            return False
    else:
        print(f"[LangSmith] Tracing disabled (set LANGCHAIN_TRACING_V2=true and LANGSMITH_API_KEY to enable)")
        return False


def run_trading_workflow(symbol: str, timeframe: str = "15m") -> Dict[str, Any]:
    """
    Run the complete trading workflow for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., "BTC/USDT:USDT")
        timeframe: Candle timeframe (e.g., "15m")
        
    Returns:
        Final state after workflow execution
    """
    # Setup tracing (optional)
    setup_langsmith_tracing()
    
    # Create graph
    app = create_trading_graph()
    
    # Initialize state
    initial_state = {
        'symbol': symbol,
        'timeframe': timeframe,
        'paper_balance': Config.INITIAL_BALANCE,
        'reasons': [],
        'notes': ''
    }
    
    # Run workflow
    try:
        final_state = app.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        return {
            **initial_state,
            'error': str(e),
            'direction': 'SKIP',
            'confidence': 0,
            'reasons': [f'Workflow error: {str(e)}']
        }
