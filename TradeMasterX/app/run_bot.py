#!/usr/bin/env python3
"""
TradeMasterX - Paper Trading Bot for Bybit Futures
Run with: python -m app.run_bot --once
          python -m app.run_bot --loop
"""
import argparse
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.graph import run_trading_workflow


def format_output(state: Dict[str, Any]) -> str:
    """
    Format state as JSON output.
    
    Args:
        state: Final workflow state
        
    Returns:
        JSON string
    """
    output = {
        'symbol': state.get('symbol'),
        'timeframe': state.get('timeframe'),
        'timestamp': state.get('timestamp'),
        'decision': state.get('direction'),
        'confidence': state.get('confidence'),
        'entry': state.get('entry'),
        'stop_loss': state.get('stop_loss'),
        'take_profit': state.get('take_profit'),
        'leverage_suggestion': state.get('leverage_suggestion'),
        'position_size_usdt': state.get('position_size_usdt'),
        'reasons': state.get('reasons', []),
        'invalidation': state.get('invalidation', ''),
        'notes': state.get('notes', ''),
        'open_position': state.get('open_position'),
        'current_price': state.get('current_price'),
        'trend': state.get('trend'),
        'rsi': state.get('rsi'),
        'error': state.get('error')
    }
    
    return json.dumps(output, indent=2)


def run_single_analysis():
    """Run analysis once for all configured symbols."""
    print("=" * 80)
    print("TradeMasterX - Bybit Futures Paper Trading Bot")
    print("=" * 80)
    print(f"Mode: Single Run")
    print(f"Symbols: {Config.SYMBOLS}")
    print(f"Timeframe: {Config.TIMEFRAME}")
    print(f"Paper Balance: ${Config.INITIAL_BALANCE:,.2f}")
    print("=" * 80)
    
    for symbol in Config.SYMBOLS:
        print(f"\n{'=' * 80}")
        print(f"Analyzing {symbol}")
        print('=' * 80)
        
        try:
            # Run workflow
            final_state = run_trading_workflow(symbol, Config.TIMEFRAME)
            
            # Print output
            print("\n" + "=" * 80)
            print("RESULT")
            print("=" * 80)
            print(format_output(final_state))
            
        except Exception as e:
            print(f"\n[ERROR] Failed to analyze {symbol}: {e}")
            continue
        
        print()


def run_loop():
    """Run analysis in a loop at configured intervals."""
    print("=" * 80)
    print("TradeMasterX - Bybit Futures Paper Trading Bot")
    print("=" * 80)
    print(f"Mode: Loop (every {Config.RUN_INTERVAL_MINUTES} minutes)")
    print(f"Symbols: {Config.SYMBOLS}")
    print(f"Timeframe: {Config.TIMEFRAME}")
    print(f"Paper Balance: ${Config.INITIAL_BALANCE:,.2f}")
    print("=" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    run_count = 0
    
    try:
        while True:
            run_count += 1
            print(f"\n{'=' * 80}")
            print(f"Run #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print('=' * 80)
            
            for symbol in Config.SYMBOLS:
                print(f"\n{'-' * 80}")
                print(f"Analyzing {symbol}")
                print('-' * 80)
                
                try:
                    # Run workflow
                    final_state = run_trading_workflow(symbol, Config.TIMEFRAME)
                    
                    # Print compact summary
                    decision = final_state.get('direction', 'SKIP')
                    confidence = final_state.get('confidence', 0)
                    price = final_state.get('current_price', 0)
                    
                    print(f"\n[{symbol}] {decision} (confidence: {confidence}%) @ ${price:,.2f}")
                    
                    if final_state.get('open_position'):
                        pos = final_state['open_position']
                        print(f"  Open Position: {pos['side']} | "
                              f"PnL: ${pos['unrealized_pnl']:+,.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
                    
                    if decision != 'SKIP':
                        reasons = final_state.get('reasons', [])
                        for reason in reasons[:2]:
                            print(f"  • {reason}")
                    
                except Exception as e:
                    print(f"\n[ERROR] Failed to analyze {symbol}: {e}")
                    continue
            
            # Wait for next interval
            print(f"\n{'=' * 80}")
            print(f"Waiting {Config.RUN_INTERVAL_MINUTES} minutes until next run...")
            print('=' * 80)
            time.sleep(Config.RUN_INTERVAL_MINUTES * 60)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Bot stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='TradeMasterX - Paper Trading Bot for Bybit Futures'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Run in loop at configured interval'
    )
    
    args = parser.parse_args()
    
    if args.loop:
        run_loop()
    elif args.once:
        run_single_analysis()
    else:
        # Default to single run
        print("No mode specified. Use --once or --loop")
        print("Running once by default...\n")
        run_single_analysis()


if __name__ == '__main__':
    main()
