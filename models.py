from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class StrategyStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class TradingMode(enum.Enum):
    PAPER = "paper"
    LIVE = "live"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    paper_balance = Column(Float, default=10000.0)
    live_balance = Column(Float, default=0.0)
    max_open_trades = Column(Integer, default=5)
    risk_per_trade = Column(Float, default=2.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    strategies = relationship('Strategy', back_populates='user', cascade='all, delete-orphan')
    trades = relationship('Trade', back_populates='user', cascade='all, delete-orphan')
    backtests = relationship('Backtest', back_populates='user', cascade='all, delete-orphan')

class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(500))
    exchange = Column(String(50), default='gemini')
    trading_pair = Column(String(20), default='btcusd')
    timeframe = Column(String(10), default='1h')
    parameters = Column(JSON, default={})
    entry_conditions = Column(JSON, default={})
    exit_conditions = Column(JSON, default={})
    stop_loss_pct = Column(Float, default=2.0)
    take_profit_pct = Column(Float, default=5.0)
    status = Column(Enum(StrategyStatus), default=StrategyStatus.DRAFT)
    trading_mode = Column(Enum(TradingMode), default=TradingMode.PAPER)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship('User', back_populates='strategies')
    backtests = relationship('Backtest', back_populates='strategy', cascade='all, delete-orphan')

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True)
    pair = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(20), default='FILLED')
    pnl = Column(Float, default=0.0)
    pnl_pct = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='trades')

class Backtest(Base):
    __tablename__ = 'backtests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    total_return_pct = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    results = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='backtests')
    strategy = relationship('Strategy', back_populates='backtests')
