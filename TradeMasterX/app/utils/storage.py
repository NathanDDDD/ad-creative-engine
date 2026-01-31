"""
SQLite storage for trade journal.
No external API dependencies.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class Storage:
    """SQLite-based storage for trade journal and runs."""
    
    def __init__(self, db_path: str = 'journal.db'):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Runs table - every execution of the bot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence INTEGER,
                entry REAL,
                stop_loss REAL,
                take_profit REAL,
                position_size_usdt REAL,
                leverage INTEGER,
                reasons TEXT,
                invalidation TEXT,
                notes TEXT,
                current_price REAL,
                trend TEXT,
                rsi REAL,
                error TEXT
            )
        ''')
        
        # Trades table - simulated trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                position_size_usdt REAL NOT NULL,
                leverage INTEGER NOT NULL,
                close_time TEXT,
                close_price REAL,
                pnl REAL,
                pnl_pct REAL,
                status TEXT NOT NULL,
                close_reason TEXT
            )
        ''')
        
        # Performance summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                avg_win_pct REAL DEFAULT 0,
                avg_loss_pct REAL DEFAULT 0,
                avg_r REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def log_run(self, state: Dict[str, Any]):
        """Log a bot run to database."""
        cursor = self.conn.cursor()
        
        reasons_json = json.dumps(state.get('reasons', []))
        
        cursor.execute('''
            INSERT INTO runs (
                timestamp, symbol, timeframe, decision, confidence,
                entry, stop_loss, take_profit, position_size_usdt, leverage,
                reasons, invalidation, notes, current_price, trend, rsi, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            state.get('timestamp', datetime.now().isoformat()),
            state.get('symbol'),
            state.get('timeframe'),
            state.get('direction'),
            state.get('confidence'),
            state.get('entry'),
            state.get('stop_loss'),
            state.get('take_profit'),
            state.get('position_size_usdt'),
            state.get('leverage_suggestion'),
            reasons_json,
            state.get('invalidation', ''),
            state.get('notes', ''),
            state.get('current_price'),
            state.get('trend'),
            state.get('rsi'),
            state.get('error')
        ))
        
        self.conn.commit()
    
    def open_trade(self, position: Dict[str, Any]) -> int:
        """
        Open a new simulated trade.
        
        Returns:
            Trade ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                symbol, side, entry_time, entry_price, stop_loss, take_profit,
                position_size_usdt, leverage, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            position['symbol'],
            position['side'],
            position['entry_time'],
            position['entry_price'],
            position['stop_loss'],
            position['take_profit'],
            position['position_size_usdt'],
            position['leverage'],
            'OPEN'
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def close_trade(self, trade_id: int, close_price: float, close_reason: str):
        """Close a trade and calculate PnL."""
        cursor = self.conn.cursor()
        
        # Get trade details
        cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
        trade = cursor.fetchone()
        
        if not trade:
            return
        
        # Calculate PnL
        entry_price = trade['entry_price']
        position_size = trade['position_size_usdt']
        side = trade['side']
        
        if side == 'LONG':
            pnl_pct = ((close_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_pct = ((entry_price - close_price) / entry_price) * 100
        
        pnl = (pnl_pct / 100) * position_size * trade['leverage']
        
        # Update trade
        cursor.execute('''
            UPDATE trades
            SET close_time = ?, close_price = ?, pnl = ?, pnl_pct = ?, 
                status = 'CLOSED', close_reason = ?
            WHERE id = ?
        ''', (
            datetime.now().isoformat(),
            close_price,
            pnl,
            pnl_pct,
            close_reason,
            trade_id
        ))
        
        self.conn.commit()
        
        # Update performance
        self._update_performance()
    
    def get_open_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get open position for a symbol if exists."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trades 
            WHERE symbol = ? AND status = 'OPEN'
            ORDER BY id DESC LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def _update_performance(self):
        """Update performance statistics."""
        cursor = self.conn.cursor()
        
        # Get closed trades stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(pnl) as total_pnl,
                AVG(CASE WHEN pnl > 0 THEN pnl_pct ELSE NULL END) as avg_win_pct,
                AVG(CASE WHEN pnl <= 0 THEN pnl_pct ELSE NULL END) as avg_loss_pct
            FROM trades WHERE status = 'CLOSED'
        ''')
        
        stats = cursor.fetchone()
        
        total = stats['total'] or 0
        wins = stats['wins'] or 0
        losses = stats['losses'] or 0
        win_rate = (wins / total * 100) if total > 0 else 0
        total_pnl = stats['total_pnl'] or 0
        avg_win = stats['avg_win_pct'] or 0
        avg_loss = stats['avg_loss_pct'] or 0
        avg_r = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Insert performance snapshot
        cursor.execute('''
            INSERT INTO performance (
                timestamp, total_trades, winning_trades, losing_trades,
                win_rate, total_pnl, avg_win_pct, avg_loss_pct, avg_r
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            total, wins, losses, win_rate, total_pnl,
            avg_win, avg_loss, avg_r
        ))
        
        self.conn.commit()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get latest performance summary."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM performance ORDER BY id DESC LIMIT 1
        ''')
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win_pct': 0,
            'avg_loss_pct': 0,
            'avg_r': 0
        }
    
    def close(self):
        """Close database connection."""
        self.conn.close()
