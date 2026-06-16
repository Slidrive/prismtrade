import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime]
    exit_price: Optional[float]
    side: OrderSide
    size: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    fees: float = 0.0
    
    def close(self, exit_time: datetime, exit_price: float, fee_pct: float = 0.001):
        self.exit_time = exit_time
        self.exit_price = exit_price
        
        if self.side == OrderSide.BUY:
            gross_pnl = (exit_price - self.entry_price) * self.size
        else:
            gross_pnl = (self.entry_price - exit_price) * self.size
        
        self.fees = (self.entry_price * self.size * fee_pct) + (exit_price * self.size * fee_pct)
        self.pnl = gross_pnl - self.fees
        self.pnl_pct = (self.pnl / (self.entry_price * self.size)) * 100

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000, fee_pct: float = 0.001, max_positions: int = 1):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.fee_pct = fee_pct
        self.max_positions = max_positions
        self.positions: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []
    
    def can_open_position(self) -> bool:
        return len(self.positions) < self.max_positions
    
    def open_position(self, timestamp: datetime, price: float, side: OrderSide, size: Optional[float] = None, risk_pct: float = 2.0):
        if not self.can_open_position():
            return False
        if size is None:
            risk_amount = self.capital * (risk_pct / 100)
            size = risk_amount / price
        position_value = price * size
        if position_value > self.capital:
            return False
        trade = Trade(entry_time=timestamp, entry_price=price, exit_time=None, exit_price=None, side=side, size=size)
        self.positions.append(trade)
        self.capital -= position_value
        return True
    
    def close_position(self, timestamp: datetime, price: float, position_idx: int = 0):
        if position_idx >= len(self.positions):
            return False
        trade = self.positions[position_idx]
        trade.close(timestamp, price, self.fee_pct)
        self.capital += (trade.exit_price * trade.size) + trade.pnl
        self.closed_trades.append(trade)
        self.positions.pop(position_idx)
        return True
    
    def update_equity(self, timestamp: datetime, current_price: float):
        unrealized_pnl = 0
        for pos in self.positions:
            if pos.side == OrderSide.BUY:
                unrealized_pnl += (current_price - pos.entry_price) * pos.size
            else:
                unrealized_pnl += (pos.entry_price - current_price) * pos.size
        total_equity = self.capital + unrealized_pnl
        self.equity_curve.append(total_equity)
        self.timestamps.append(timestamp)
    
    def get_stats(self) -> Dict:
        if not self.closed_trades:
            return {'total_trades': 0, 'error': 'No closed trades'}
        trades_df = pd.DataFrame([{'entry_time': t.entry_time, 'exit_time': t.exit_time, 'entry_price': t.entry_price, 'exit_price': t.exit_price, 'pnl': t.pnl, 'pnl_pct': t.pnl_pct, 'side': t.side.value} for t in self.closed_trades])
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] <= 0]
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        if len(self.equity_curve) > 1:
            returns = equity_series.pct_change().dropna()
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe = 0
        stats = {'total_trades': len(self.closed_trades), 'winning_trades': len(winning_trades), 'losing_trades': len(losing_trades), 'win_rate': (len(winning_trades) / len(self.closed_trades)) * 100 if self.closed_trades else 0, 'total_pnl': trades_df['pnl'].sum(), 'total_return_pct': ((self.capital - self.initial_capital) / self.initial_capital) * 100, 'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0, 'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0, 'largest_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0, 'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0, 'profit_factor': abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0, 'max_drawdown_pct': max_drawdown, 'sharpe_ratio': sharpe, 'final_capital': self.capital, 'initial_capital': self.initial_capital}
        return stats
    
    def print_report(self):
        stats = self.get_stats()
        if 'error' in stats:
            print(f"\n❌ {stats['error']}")
            return
        print("\n" + "="*60)
        print("📊 BACKTEST RESULTS")
        print("="*60)
        print(f"\n💰 CAPITAL:")
        print(f"  Initial:        ${stats['initial_capital']:,.2f}")
        print(f"  Final:          ${stats['final_capital']:,.2f}")
        print(f"  Total P&L:      ${stats['total_pnl']:,.2f}")
        print(f"  Return:         {stats['total_return_pct']:.2f}%")
        print(f"\n📈 TRADES:")
        print(f"  Total:          {stats['total_trades']}")
        print(f"  Winners:        {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
        print(f"  Losers:         {stats['losing_trades']}")
        print(f"\n🎯 PERFORMANCE:")
        print(f"  Avg Win:        ${stats['avg_win']:,.2f}")
        print(f"  Avg Loss:       ${stats['avg_loss']:,.2f}")
        print(f"  Largest Win:    ${stats['largest_win']:,.2f}")
        print(f"  Largest Loss:   ${stats['largest_loss']:,.2f}")
        print(f"  Profit Factor:  {stats['profit_factor']:.2f}")
        print(f"\n📉 RISK METRICS:")
        print(f"  Max Drawdown:   {stats['max_drawdown_pct']:.2f}%")
        print(f"  Sharpe Ratio:   {stats['sharpe_ratio']:.2f}")
        print("\n" + "="*60)

def simple_ma_crossover_strategy(df: pd.DataFrame, fast_period: int = 10, slow_period: int = 30) -> pd.DataFrame:
    df = df.copy()
    df['ma_fast'] = df['close'].rolling(window=fast_period).mean()
    df['ma_slow'] = df['close'].rolling(window=slow_period).mean()
    df['signal'] = 0
    df.loc[df['ma_fast'] > df['ma_slow'], 'signal'] = 1
    df.loc[df['ma_fast'] < df['ma_slow'], 'signal'] = -1
    df['position'] = df['signal'].diff()
    return df

def run_backtest_example():
    from market_data import MarketDataProvider
    print("🔄 Fetching historical data...")
    provider = MarketDataProvider()
    df = provider.get_ohlcv('bitcoin', days=30)
    print(f"✅ Loaded {len(df)} candles")
    df = simple_ma_crossover_strategy(df, fast_period=10, slow_period=30)
    engine = BacktestEngine(initial_capital=10000, fee_pct=0.001, max_positions=1)
    print("🚀 Running backtest...")
    for idx, row in df.iterrows():
        timestamp = row['timestamp']
        price = row['close']
        if row['position'] == 2 and engine.can_open_position():
            engine.open_position(timestamp, price, OrderSide.BUY, risk_pct=10)
            print(f"  📈 BUY @ ${price:,.2f} on {timestamp}")
        elif row['position'] == -2 and len(engine.positions) > 0:
            engine.close_position(timestamp, price)
            print(f"  📉 SELL @ ${price:,.2f} on {timestamp}")
        engine.update_equity(timestamp, price)
    if engine.positions:
        last_price = df.iloc[-1]['close']
        last_time = df.iloc[-1]['timestamp']
        engine.close_position(last_time, last_price)
    engine.print_report()

if __name__ == "__main__":
    run_backtest_example()
