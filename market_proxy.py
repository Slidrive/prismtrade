"""Server-side market data proxy.

The browser cannot call api.binance.com directly (CORS + US geo-block returns 451).
So the backend fetches public OHLCV/price server-side and the frontend reads it
same-origin. We use Binance.US, which is reachable from US-hosted servers and needs
no API key for public market data.
"""
import ccxt

_QUOTES = ('USDT', 'USDC', 'USD', 'BTC', 'ETH')


def to_ccxt_symbol(symbol: str) -> str:
    """'BTCUSDT' -> 'BTC/USDT'. Pass-through if already slashed."""
    if '/' in symbol:
        return symbol
    for q in _QUOTES:
        if symbol.endswith(q):
            return f"{symbol[:-len(q)]}/{q}"
    return symbol


def _exchange():
    # binanceus: US-legal, public data needs no key, has USDT pairs.
    return ccxt.binanceus({'enableRateLimit': True})


def fetch_candles(symbol: str, timeframe: str = '1m', limit: int = 500):
    """Returns a list of [ms, open, high, low, close, volume]."""
    ex = _exchange()
    return ex.fetch_ohlcv(to_ccxt_symbol(symbol), timeframe, limit=limit)


def fetch_last_price(symbol: str):
    ex = _exchange()
    return float(ex.fetch_ticker(to_ccxt_symbol(symbol))['last'])
