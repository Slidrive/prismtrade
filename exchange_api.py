import ccxt
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd

class ExchangeAPI:
    """Unified exchange API wrapper using CCXT"""
    
    def __init__(self, exchange_name: str, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None, testnet: bool = True):
        self.exchange_name = exchange_name.lower()
        
        # Initialize exchange
        exchange_class = getattr(ccxt, self.exchange_name)
        
        config = {
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        }
        
        if api_key and api_secret:
            config['apiKey'] = api_key
            config['secret'] = api_secret
        
        if testnet:
            config['options']['sandboxMode'] = True
        
        self.exchange = exchange_class(config)
        
    def get_ticker(self, symbol: str) -> Dict:
        """Get current price and 24h stats for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last_price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume_24h': ticker['baseVolume'],
                'change_24h': ticker['change'],
                'change_pct_24h': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            raise Exception(f"Error fetching ticker for {symbol}: {str(e)}")
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                   limit: int = 100) -> pd.DataFrame:
        """Get historical OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            raise Exception(f"Error fetching OHLCV for {symbol}: {str(e)}")
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get current orderbook"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            raise Exception(f"Error fetching orderbook for {symbol}: {str(e)}")
    
    def get_balance(self) -> Dict:
        """Get account balance (requires API keys)"""
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used']
            }
        except Exception as e:
            raise Exception(f"Error fetching balance: {str(e)}")
    
    def get_markets(self) -> List[str]:
        """Get all available trading pairs"""
        try:
            markets = self.exchange.load_markets()
            return sorted(list(markets.keys()))
        except Exception as e:
            raise Exception(f"Error fetching markets: {str(e)}")
    
    def create_order(self, symbol: str, side: str, order_type: str, 
                     amount: float, price: Optional[float] = None) -> Dict:
        """Create order (requires API keys)"""
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': order['amount'],
                'price': order['price'],
                'status': order['status'],
                'timestamp': order['timestamp']
            }
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}")
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders (requires API keys)"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return [{
                'id': o['id'],
                'symbol': o['symbol'],
                'side': o['side'],
                'type': o['type'],
                'amount': o['amount'],
                'price': o['price'],
                'status': o['status'],
                'timestamp': o['timestamp']
            } for o in orders]
        except Exception as e:
            raise Exception(f"Error fetching open orders: {str(e)}")
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Cancel an order (requires API keys)"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            return {
                'id': result['id'],
                'status': result['status'],
                'message': 'Order cancelled successfully'
            }
        except Exception as e:
            raise Exception(f"Error cancelling order: {str(e)}")

# Convenience functions for common exchanges

def get_binance(api_key=None, api_secret=None, testnet=True):
    return ExchangeAPI('binance', api_key, api_secret, testnet)

def get_gemini(api_key=None, api_secret=None, testnet=True):
    return ExchangeAPI('gemini', api_key, api_secret, testnet)

def get_coinbase(api_key=None, api_secret=None, testnet=True):
    return ExchangeAPI('coinbase', api_key, api_secret, testnet)
