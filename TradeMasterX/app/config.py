"""
Configuration for TradeMasterX trading bot.
Uses only FREE/PUBLIC APIs - no API keys required.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Trading bot configuration."""
    
    # LangSmith tracing (OPTIONAL - defaults to disabled)
    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY', '')
    LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'TradeMasterX')
    
    # Paper trading settings
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '10000.0'))
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', '0.01'))  # 1%
    MIN_RISK_REWARD = float(os.getenv('MIN_RISK_REWARD', '1.5'))
    PREFERRED_RISK_REWARD = float(os.getenv('PREFERRED_RISK_REWARD', '2.0'))
    
    # Trading symbols
    SYMBOLS_STR = os.getenv('SYMBOLS', 'BTC/USDT:USDT,ETH/USDT:USDT,SOL/USDT:USDT')
    SYMBOLS: List[str] = [s.strip() for s in SYMBOLS_STR.split(',')]
    
    # Timeframe
    TIMEFRAME = os.getenv('TIMEFRAME', '15m')
    LOOKBACK_PERIODS = 200
    
    # Run interval
    RUN_INTERVAL_MINUTES = int(os.getenv('RUN_INTERVAL_MINUTES', '15'))
    
    # Indicator settings
    EMA_FAST = 50
    EMA_SLOW = 200
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    
    # Risk management
    MAX_LEVERAGE = 10
    MIN_CONFIDENCE = 60  # Minimum confidence to take a trade
    
    # Database
    DB_PATH = 'journal.db'
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if cls.LANGCHAIN_TRACING_V2 and not cls.LANGSMITH_API_KEY:
            print("WARNING: LANGCHAIN_TRACING_V2 enabled but LANGSMITH_API_KEY not set.")
            print("Tracing will be disabled.")
            cls.LANGCHAIN_TRACING_V2 = False
        
        return True


# Validate on import
Config.validate()
