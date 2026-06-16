import ccxt
from api_key_manager import key_manager
from models import APIKey
from database import DBSession

class ExchangeConnector:
    def __init__(self, user_id, exchange_name='gemini'):
        self.user_id = user_id
        self.exchange_name = exchange_name.lower()
        self.exchange = None
        
    def connect(self):
        '''Connect to exchange using encrypted API keys'''
        with DBSession() as db:
            api_key = db.query(APIKey).filter(
                APIKey.user_id == self.user_id,
                APIKey.exchange == self.exchange_name,
                APIKey.is_active == True
            ).first()
            
            if not api_key:
                raise Exception(f'No active API key found for {self.exchange_name}')
            
            # Decrypt keys
            key = key_manager.decrypt(api_key.encrypted_key)
            secret = key_manager.decrypt(api_key.encrypted_secret)
            
            # Initialize exchange
            exchange_class = getattr(ccxt, self.exchange_name)
            self.exchange = exchange_class({
                'apiKey': key,
                'secret': secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            
            return self.exchange
    
    def get_balance(self):
        '''Get account balance'''
        if not self.exchange:
            self.connect()
        return self.exchange.fetch_balance()
    
    def create_market_buy(self, symbol, amount):
        '''Execute market buy order'''
        if not self.exchange:
            self.connect()
        return self.exchange.create_market_buy_order(symbol, amount)
    
    def create_market_sell(self, symbol, amount):
        '''Execute market sell order'''
        if not self.exchange:
            self.connect()
        return self.exchange.create_market_sell_order(symbol, amount)
    
    def get_ticker(self, symbol):
        '''Get current price for symbol'''
        if not self.exchange:
            self.connect()
        return self.exchange.fetch_ticker(symbol)
    
    def get_open_orders(self, symbol=None):
        '''Get all open orders'''
        if not self.exchange:
            self.connect()
        return self.exchange.fetch_open_orders(symbol)
