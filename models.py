from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class StrategyStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class BacktestStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TradeStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TradingMode(enum.Enum):
    PAPER = "paper"
    LIVE = "live"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FREE)
    paper_balance = Column(Float, default=10000.0)
    live_balance = Column(Float, default=0.0)
    max_open_trades = Column(Integer, default=3)
    risk_per_trade = Column(Float, default=2.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    exchanges = relationship("ExchangeConnection", back_populates="user", cascade="all, delete-orphan")
    backtests = relationship("Backtest", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")

class ExchangeConnection(Base):
    __tablename__ = 'exchange_connections'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exchange_name = Column(String(50), nullable=False)
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    is_testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    user = relationship("User", back_populates="exchanges")

class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    exchange = Column(String(50), nullable=False)
    trading_pair = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    parameters = Column(JSON, nullable=False)
    entry_conditions = Column(JSON)
    exit_conditions = Column(JSON)
    stop_loss_pct = Column(Float)
    take_profit_pct = Column(Float)
    trailing_stop = Column(Boolean, default=False)
    status = Column(Enum(StrategyStatus), default=StrategyStatus.DRAFT)
    trading_mode = Column(Enum(TradingMode), default=TradingMode.PAPER)
    source_type = Column(String(50))
    source_data = Column(JSON)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="strategies")
    backtests = relationship("Backtest", back_populates="strategy", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="strategy", cascade="all, delete-orphan")

class Backtest(Base):
    __tablename__ = 'backtests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_balance = Column(Float, nullable=False)
    status = Column(Enum(BacktestStatus), default=BacktestStatus.PENDING)
    final_balance = Column(Float)
    total_return_pct = Column(Float)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    avg_win = Column(Float)
    avg_loss = Column(Float)
    largest_win = Column(Float)
    largest_loss = Column(Float)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    results_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    user = relationship("User", back_populates="backtests")
    strategy = relationship("Strategy", back_populates="backtests")

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    exchange_order_id = Column(String(100))
    trading_pair = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_amount = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_price = Column(Float)
    exit_amount = Column(Float)
    exit_time = Column(DateTime)
    profit_loss = Column(Float)
    profit_loss_pct = Column(Float)
    fees = Column(Float, default=0.0)
    status = Column(Enum(TradeStatus), default=TradeStatus.OPEN)
    trading_mode = Column(Enum(TradingMode), nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    exit_reason = Column(String(100))
    notes = Column(Text)
    trade_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
