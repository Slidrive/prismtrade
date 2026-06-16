import requests
import pandas as pd
from datetime import datetime, timedelta

class MarketDataProvider:
    """Alternative market data using CoinGecko (no API key needed)"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_ticker(self, coin='bitcoin', vs_currency='usd'):
        """Get current price"""
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': coin,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_last_updated_at': 'true'
        }
        r = requests.get(url, params=params)
        data = r.json()[coin]
        
        return {
            'symbol': f'{coin.upper()}/{vs_currency.upper()}',
            'last_price': data[vs_currency],
            'change_24h': data.get(f'{vs_currency}_24h_change', 0),
            'volume_24h': data.get(f'{vs_currency}_24h_vol', 0),
            'timestamp': data.get('last_updated_at', int(datetime.now().timestamp()))
        }
    
    def get_ohlcv(self, coin='bitcoin', vs_currency='usd', days=7):
        """Get historical OHLCV data"""
        url = f"{self.base_url}/coins/{coin}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        r = requests.get(url, params=params)
        data = r.json()
        
        # Debug: Check what we got
        if 'prices' not in data:
            raise Exception(f"API Error: {data}")
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'timestamp': [pd.Timestamp(x[0], unit='ms') for x in data['prices']],
            'close': [x[1] for x in data['prices']]
        })
        
        if 'total_volumes' in data:
            df['volume'] = [x[1] for x in data['total_volumes']]
        
        # Create OHLCV by resampling to hourly candles
        df.set_index('timestamp', inplace=True)
        
        ohlcv = pd.DataFrame()
        ohlcv['open'] = df['close'].resample('1h').first()
        ohlcv['high'] = df['close'].resample('1h').max()
        ohlcv['low'] = df['close'].resample('1h').min()
        ohlcv['close'] = df['close'].resample('1h').last()
        if 'volume' in df.columns:
            ohlcv['volume'] = df['volume'].resample('1h').sum()
        
        ohlcv.dropna(inplace=True)
        ohlcv.reset_index(inplace=True)
        
        return ohlcv
    
    def get_supported_coins(self):
        """Get list of supported coins"""
        url = f"{self.base_url}/coins/list"
        r = requests.get(url)
        return r.json()[:100]

# Quick test function
if __name__ == "__main__":
    provider = MarketDataProvider()
    print("\n📊 BTC Current Price:")
    print(provider.get_ticker('bitcoin'))
    print("\n📈 BTC 7-Day History (first 5 rows):")
    df = provider.get_ohlcv('bitcoin', days=7)
    print(df.head())
    print(f"\nTotal candles: {len(df)}")
