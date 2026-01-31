#!/usr/bin/env python3
"""
Entry point for TradeMasterX bot.
"""
import sys
import os

# Add TradeMasterX directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from app.run_bot import main

if __name__ == '__main__':
    main()
