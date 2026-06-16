================================================================================
PRISMTRADE - POWERSHELL COMMAND REFERENCE
Complete Step-by-Step Commands for Windows
================================================================================

PHASE 1: SECURE API KEY STORAGE

CREATE FILE 1: api_key_manager.py
$content = @''
from cryptography.fernet import Fernet
import os

class APIKeyManager:
    def __init__(self, master_key=None):
        if master_key is None:
            master_key = os.getenv("MASTER_KEY")
        self.cipher_suite = Fernet(master_key)
    
    @staticmethod
    def generate_master_key():
        return Fernet.generate_key().decode()
    
    def encrypt_key(self, api_key):
        return self.cipher_suite.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key):
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
''@
$content | Out-File api_key_manager.py -Encoding utf8

CREATE FILE 2: live_trading.py
$content = @''
import ccxt
from api_key_manager import APIKeyManager
from models import APIKey, Trade
from app import db

class LiveTrader:
    def __init__(self, user_id, exchange_name):
        self.user_id = user_id
        self.exchange_name = exchange_name
        self.api_key_obj = APIKey.query.filter_by(user_id=user_id, exchange=exchange_name).first()
        
        if not self.api_key_obj:
            raise Exception("No API keys found")
        
        manager = APIKeyManager()
        api_key = manager.decrypt_key(self.api_key_obj.encrypted_key)
        api_secret = manager.decrypt_key(self.api_key_obj.encrypted_secret)
        
        self.exchange = getattr(ccxt, exchange_name.lower())({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True
        })
    
    def place_order(self, symbol, side, amount, price=None, order_type="market"):
        try:
            if order_type == "market":
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            return {"success": True, "order": order}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_balance(self):
        return self.exchange.fetch_balance()
''@
$content | Out-File live_trading.py -Encoding utf8

INSTALL DEPENDENCIES:
pip install cryptography==41.0.0 ccxt==4.0.0

GENERATE MASTER KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

CREATE .env FILE:
@''
MASTER_KEY=paste_your_key_here
FLASK_ENV=development
''@ | Out-File .env -Encoding utf8

LOCAL TESTING:
Terminal 1: python app.py
Terminal 2: cd frontend && npm start
Terminal 3: curl http://localhost:5000/api/health

DEPLOY:
git add .
git commit -m "Phase 1: Secure API keys"
git push origin main

================================================================================
