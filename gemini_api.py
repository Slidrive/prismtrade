import requests
from datetime import datetime, timedelta

GEMINI_API = "https://api.gemini.com/v1"

class GeminiAPI:
    def __init__(self):
        self.base_url = GEMINI_API
        self.session = requests.Session()
    
    def get_ticker(self, pair):
        try:
            url = f"{self.base_url}/pubticker/{pair}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            return {'pair': pair, 'price': float(data.get('last', 0)), 'bid': float(data.get('bid', 0)), 'ask': float(data.get('ask', 0))}
        except:
            return None
    
    def get_candles(self, pair, timeframe='1h', limit=100):
        try:
            url = f"{self.base_url}/candles/{pair}/{timeframe}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                candles = response.json()
                return [{'time': int(c[0]/1000), 'open': float(c[1]), 'high': float(c[2]), 'low': float(c[3]), 'close': float(c[4]), 'volume': float(c[5])} for c in candles]
        except:
            pass
        return []

gemini = GeminiAPI()