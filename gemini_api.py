import requests
from datetime import datetime, timedelta

GEMINI_API = "https://api.gemini.com/v1"
TIMEFRAME_MAP = {'1m': 60, '5m': 300, '15m': 900, '1h': 3600, '4h': 14400, '1d': 86400}

class GeminiAPI:
    def __init__(self):
        self.base_url = GEMINI_API
        self.session = requests.Session()
    
    def get_ticker(self, pair):
        try:
            url = f"{self.base_url}/pubticker/{pair}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {'pair': pair, 'price': float(data.get('last', 0)), 'bid': float(data.get('bid', 0)), 'ask': float(data.get('ask', 0)), 'volume': float(data.get('volume', {}).get('BTC' if 'btc' in pair.lower() else 'ETH', 0)), 'timestamp': datetime.utcnow().isoformat()}
        except Exception as e:
            print(f"Error fetching ticker: {str(e)}")
            return None
    
    def get_candles(self, pair, timeframe='1h', limit=100):
        try:
            url = f"{self.base_url}/candles/{pair}/{timeframe}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                candles = response.json()
                return [{'time': int(candle[0] / 1000), 'open': float(candle[1]), 'high': float(candle[2]), 'low': float(candle[3]), 'close': float(candle[4]), 'volume': float(candle[5])} for candle in candles]
            else:
                return self._generate_mock_candles(pair, timeframe, limit)
        except Exception as e:
            print(f"Error fetching candles: {str(e)}")
            return self._generate_mock_candles(pair, timeframe, limit)
    
    def _generate_mock_candles(self, pair, timeframe='1h', limit=100):
        try:
            ticker = self.get_ticker(pair)
            if not ticker:
                return []
            current_price = ticker['price']
            candles = []
            now = datetime.utcnow()
            timeframe_seconds = TIMEFRAME_MAP.get(timeframe, 3600)
            for i in range(limit):
                timestamp = int((now - timedelta(seconds=timeframe_seconds * i)).timestamp())
                open_price = current_price * (0.98 + (i % 5) * 0.004)
                close_price = open_price * (0.99 + (i % 3) * 0.005)
                high_price = max(open_price, close_price) * 1.01
                low_price = min(open_price, close_price) * 0.99
                volume = 1000 + (i % 500) * 10
                candles.insert(0, {'time': timestamp, 'open': round(open_price, 2), 'high': round(high_price, 2), 'low': round(low_price, 2), 'close': round(close_price, 2), 'volume': volume})
            return candles
        except Exception as e:
            print(f"Error generating mock candles: {str(e)}")
            return []

gemini = GeminiAPI()
