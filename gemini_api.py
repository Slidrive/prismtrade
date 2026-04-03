import requests
import time
import random

# Realistic mock prices for common trading pairs (used as fallback)
_MOCK_PRICES = {
    "btcusd": 67_420.00,
    "ethusd": 3_512.50,
    "solusd": 172.30,
    "ltcusd": 84.15,
    "bchusd": 478.90,
}

def _mock_price(pair):
    base = _MOCK_PRICES.get(pair, 100.0)
    # Add a small random jitter so repeated calls look live
    return round(base * (1 + random.uniform(-0.002, 0.002)), 2)


class GeminiAPI:
    def __init__(self):
        self.base_url = "https://api.gemini.com/v1"
        self.session = requests.Session()

    def get_ticker(self, pair):
        """Return ticker data for a trading pair.

        Attempts to fetch live data from the Gemini public API.
        Falls back to mock data if the request fails.
        """
        try:
            url = f"{self.base_url}/pubticker/{pair}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {
                "pair": pair,
                "price": float(data.get("last", 0)),
                "bid": float(data.get("bid", 0)),
                "ask": float(data.get("ask", 0)),
                "volume": data.get("volume", {}),
                "source": "live",
            }
        except Exception:
            price = _mock_price(pair)
            return {
                "pair": pair,
                "price": price,
                "bid": round(price * 0.9995, 2),
                "ask": round(price * 1.0005, 2),
                "volume": {"USD": "0", pair[:3].upper(): "0"},
                "source": "mock",
            }

    def get_candles(self, pair, timeframe="1hr", limit=100):
        """Return candlestick (OHLCV) data for a trading pair.

        Attempts to fetch live data from the Gemini public API.
        Falls back to generated mock candles if the request fails.
        Valid Gemini timeframes: 1m, 5m, 15m, 30m, 1hr, 6hr, 1day.
        """
        try:
            url = f"{self.base_url}/candles/{pair}/{timeframe}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            raw = response.json()
            # Gemini returns [[timestamp, open, high, low, close, volume], ...]
            candles = [
                {
                    "timestamp": c[0],
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5],
                }
                for c in raw[:limit]
            ]
            return candles
        except Exception:
            return self._mock_candles(pair, limit)

    def _mock_candles(self, pair, limit=100):
        """Generate realistic-looking mock OHLCV candles."""
        base_price = _mock_price(pair)
        candles = []
        now_ms = int(time.time() * 1000)
        interval_ms = 3_600_000  # 1 hour in milliseconds

        price = base_price
        for i in range(limit, 0, -1):
            ts = now_ms - i * interval_ms
            open_ = round(price, 2)
            close = round(price * (1 + random.uniform(-0.015, 0.015)), 2)
            high = round(max(open_, close) * (1 + random.uniform(0, 0.008)), 2)
            low = round(min(open_, close) * (1 - random.uniform(0, 0.008)), 2)
            volume = round(random.uniform(10, 500), 4)
            candles.append({
                "timestamp": ts,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            })
            price = close  # walk forward from the last close

        return candles


gemini = GeminiAPI()
