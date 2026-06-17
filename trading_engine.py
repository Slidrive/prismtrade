from exchange_connector import ExchangeConnector
from models import Trade, Strategy, User, TradingMode, TradeStatus
from database import DBSession
from datetime import datetime
import logging
import ccxt

logger = logging.getLogger(__name__)

# Realistic taker fee applied to PAPER fills so demo P&L reflects real costs.
PAPER_FEE_RATE = 0.001  # 0.10%

class TradingEngine:
    """Core trading engine.

    PAPER mode: simulated fills at the live mark price against the user's
    paper_balance — no exchange API key required, no real funds.
    LIVE mode:  real orders via the user's encrypted exchange API key (CCXT).
    """

    def __init__(self, user_id: int, exchange: str = 'gemini'):
        self.user_id = user_id
        self.exchange = exchange
        self.connector = ExchangeConnector(user_id, exchange)

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _to_ccxt_symbol(symbol: str) -> str:
        """'BTCUSDT' -> 'BTC/USDT' (CCXT format). Pass-through if already slashed."""
        if '/' in symbol:
            return symbol
        for quote in ('USDT', 'USDC', 'USD', 'BTC', 'ETH', 'BNB'):
            if symbol.endswith(quote):
                return f"{symbol[:-len(quote)]}/{quote}"
        return symbol

    def _public_price(self, symbol: str):
        """Live price from public market data — no API key needed (for PAPER).
        Uses the self-healing market_proxy (Binance.US / Kraken / Coinbase fallback)."""
        try:
            import market_proxy
            return market_proxy.fetch_last_price(symbol)
        except Exception as e:
            logger.warning(f"public price fetch failed for {symbol}: {e}")
            return None
    
    def execute_buy(self, symbol: str, amount: float, strategy_id: int = None,
                    stop_loss_pct: float = None, take_profit_pct: float = None,
                    mode: str = 'paper', price: float = None) -> dict:
        """Execute market buy. mode='paper' simulates; mode='live' hits the exchange."""
        try:
            is_paper = (mode != 'live')

            if is_paper:
                entry_price = float(price) if price else self._public_price(symbol)
                if not entry_price:
                    raise Exception("Could not determine a price for the paper fill")
                order = {'id': None, 'status': 'filled', 'paper': True}
            else:
                self.connector.connect()
                ticker = self.connector.get_ticker(symbol)
                entry_price = ticker['last']
                order = self.connector.create_market_buy(symbol, amount)

            fee = entry_price * amount * PAPER_FEE_RATE
            stop_loss = entry_price * (1 - stop_loss_pct / 100) if stop_loss_pct else None
            take_profit = entry_price * (1 + take_profit_pct / 100) if take_profit_pct else None

            with DBSession() as db:
                if is_paper:
                    user = db.query(User).filter(User.id == self.user_id).first()
                    cost = entry_price * amount + fee
                    if user.paper_balance is None:
                        user.paper_balance = 10000.0
                    if cost > user.paper_balance:
                        raise Exception(
                            f"Insufficient paper balance: need ${cost:,.2f}, have ${user.paper_balance:,.2f}")
                    user.paper_balance -= cost

                trade = Trade(
                    user_id=self.user_id,
                    strategy_id=strategy_id,
                    exchange_order_id=order.get('id'),
                    trading_pair=symbol,
                    side='buy',
                    entry_price=entry_price,
                    entry_amount=amount,
                    entry_time=datetime.utcnow(),
                    trading_mode=TradingMode.PAPER if is_paper else TradingMode.LIVE,
                    status=TradeStatus.OPEN,
                    fees=fee,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                )
                db.add(trade)
                db.commit()
                db.refresh(trade)

                return {
                    'success': True,
                    'mode': 'paper' if is_paper else 'live',
                    'trade_id': trade.id,
                    'order': order,
                    'entry_price': entry_price,
                    'amount': amount,
                    'fee': fee,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'paper_balance': (db.query(User).filter(User.id == self.user_id).first().paper_balance
                                      if is_paper else None),
                }

        except Exception as e:
            logger.error(f"Buy order failed: {str(e)}")
            raise Exception(f"Failed to execute buy order: {str(e)}")
    
    def execute_sell(self, symbol: str, amount: float, trade_id: int = None,
                     mode: str = 'paper', price: float = None) -> dict:
        """Execute market sell / close a position. Paper credits proceeds + P&L to paper_balance."""
        try:
            is_paper = (mode != 'live')

            if is_paper:
                exit_price = float(price) if price else self._public_price(symbol)
                if not exit_price:
                    raise Exception("Could not determine a price for the paper fill")
                order = {'id': None, 'status': 'filled', 'paper': True}
            else:
                self.connector.connect()
                ticker = self.connector.get_ticker(symbol)
                exit_price = ticker['last']
                order = self.connector.create_market_sell(symbol, amount)

            with DBSession() as db:
                # For paper with no explicit trade_id, close the most recent matching open position.
                trade = None
                if trade_id:
                    trade = db.query(Trade).filter(
                        Trade.id == trade_id, Trade.user_id == self.user_id).first()
                elif is_paper:
                    trade = db.query(Trade).filter(
                        Trade.user_id == self.user_id,
                        Trade.trading_pair == symbol,
                        Trade.trading_mode == TradingMode.PAPER,
                        Trade.status == TradeStatus.OPEN,
                    ).order_by(Trade.entry_time.desc()).first()
                    if not trade:
                        raise Exception(f"No open paper position in {symbol} to sell")

                fee = exit_price * amount * PAPER_FEE_RATE

                if trade:
                    trade.exit_price = exit_price
                    trade.exit_amount = amount
                    trade.exit_time = datetime.utcnow()
                    trade.status = TradeStatus.CLOSED
                    trade.fees = (trade.fees or 0.0) + fee
                    if trade.side == 'buy':
                        trade.profit_loss = (exit_price - trade.entry_price) * amount - trade.fees
                        trade.profit_loss_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100
                    trade.exit_reason = 'manual_close'

                    if is_paper:
                        user = db.query(User).filter(User.id == self.user_id).first()
                        user.paper_balance = (user.paper_balance or 0.0) + (exit_price * amount - fee)

                db.commit()

                return {
                    'success': True,
                    'mode': 'paper' if is_paper else 'live',
                    'order': order,
                    'exit_price': exit_price,
                    'amount': amount,
                    'fee': fee,
                    'trade_id': trade.id if trade else None,
                    'profit_loss': trade.profit_loss if trade else None,
                    'paper_balance': (db.query(User).filter(User.id == self.user_id).first().paper_balance
                                      if is_paper else None),
                }

        except Exception as e:
            logger.error(f"Sell order failed: {str(e)}")
            raise Exception(f"Failed to execute sell order: {str(e)}")
    
    def get_balance(self) -> dict:
        """Get account balance"""
        try:
            self.connector.connect()
            balance = self.connector.get_balance()
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise Exception(f"Failed to get balance: {str(e)}")
    
    def get_open_positions(self) -> list:
        """Get all open positions for user"""
        try:
            with DBSession() as db:
                trades = db.query(Trade).filter(
                    Trade.user_id == self.user_id,
                    Trade.status == TradeStatus.OPEN,
                    Trade.trading_mode == TradingMode.LIVE
                ).all()
                
                positions = []
                for trade in trades:
                    # Get current price
                    try:
                        self.connector.connect()
                        ticker = self.connector.get_ticker(trade.trading_pair)
                        current_price = ticker['last']
                        
                        # Calculate unrealized P&L
                        if trade.side == 'buy':
                            unrealized_pnl = (current_price - trade.entry_price) * trade.entry_amount
                            unrealized_pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                        else:
                            unrealized_pnl = (trade.entry_price - current_price) * trade.entry_amount
                            unrealized_pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                        
                        positions.append({
                            'trade_id': trade.id,
                            'symbol': trade.trading_pair,
                            'side': trade.side,
                            'entry_price': trade.entry_price,
                            'current_price': current_price,
                            'amount': trade.entry_amount,
                            'unrealized_pnl': unrealized_pnl,
                            'unrealized_pnl_pct': unrealized_pnl_pct,
                            'stop_loss': trade.stop_loss,
                            'take_profit': trade.take_profit,
                            'entry_time': trade.entry_time.isoformat()
                        })
                    except:
                        # Skip if can't get current price
                        continue
                
                return positions
        
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            raise Exception(f"Failed to get positions: {str(e)}")
    
    def get_trade_history(self, limit: int = 50) -> list:
        """Get closed trade history"""
        try:
            with DBSession() as db:
                trades = db.query(Trade).filter(
                    Trade.user_id == self.user_id,
                    Trade.status == TradeStatus.CLOSED,
                    Trade.trading_mode == TradingMode.LIVE
                ).order_by(Trade.exit_time.desc()).limit(limit).all()
                
                history = []
                for trade in trades:
                    history.append({
                        'trade_id': trade.id,
                        'symbol': trade.trading_pair,
                        'side': trade.side,
                        'entry_price': trade.entry_price,
                        'exit_price': trade.exit_price,
                        'amount': trade.entry_amount,
                        'profit_loss': trade.profit_loss,
                        'profit_loss_pct': trade.profit_loss_pct,
                        'entry_time': trade.entry_time.isoformat(),
                        'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                        'exit_reason': trade.exit_reason
                    })
                
                return history
        
        except Exception as e:
            logger.error(f"Failed to get trade history: {str(e)}")
            raise Exception(f"Failed to get trade history: {str(e)}")
    
    def check_stop_loss_take_profit(self, trade_id: int) -> dict:
        """Check if stop loss or take profit has been hit"""
        try:
            with DBSession() as db:
                trade = db.query(Trade).filter(
                    Trade.id == trade_id,
                    Trade.user_id == self.user_id,
                    Trade.status == TradeStatus.OPEN
                ).first()
                
                if not trade:
                    return {'action': 'none', 'reason': 'trade_not_found'}
                
                # Get current price
                self.connector.connect()
                ticker = self.connector.get_ticker(trade.trading_pair)
                current_price = ticker['last']
                
                # Check stop loss
                if trade.stop_loss and current_price <= trade.stop_loss:
                    return {
                        'action': 'close',
                        'reason': 'stop_loss_hit',
                        'current_price': current_price,
                        'trigger_price': trade.stop_loss
                    }
                
                # Check take profit
                if trade.take_profit and current_price >= trade.take_profit:
                    return {
                        'action': 'close',
                        'reason': 'take_profit_hit',
                        'current_price': current_price,
                        'trigger_price': trade.take_profit
                    }
                
                return {'action': 'none', 'reason': 'no_trigger'}
        
        except Exception as e:
            logger.error(f"Failed to check SL/TP: {str(e)}")
            return {'action': 'none', 'reason': 'error', 'error': str(e)}
    
    def close_position(self, trade_id: int, reason: str = 'manual') -> dict:
        """Close an open position"""
        try:
            with DBSession() as db:
                trade = db.query(Trade).filter(
                    Trade.id == trade_id,
                    Trade.user_id == self.user_id,
                    Trade.status == TradeStatus.OPEN
                ).first()
                
                if not trade:
                    raise Exception("Trade not found or already closed")
                
                # Execute sell order
                result = self.execute_sell(
                    symbol=trade.trading_pair,
                    amount=trade.entry_amount,
                    trade_id=trade_id
                )
                
                return result
        
        except Exception as e:
            logger.error(f"Failed to close position: {str(e)}")
            raise Exception(f"Failed to close position: {str(e)}")
