"""Server-side market data proxy.

The browser cannot call api.binance.com directly (CORS + US geo-block returns 451),
so the backend fetches public OHLCV/price server-side and the frontend reads it
same-origin.

Self-healing source selection: we try several public exchanges in order and cache
whichever one actually works from this server, so we don't depend on any single
provider being reachable from a given region.
"""
import ccxt

# Tried in order. Binance.US / Kraken / Coinbase are all reachable from US servers
# and need no API key for public market data.
_CANDIDATES = ['binanceus', 'kraken', 'coinbase']
_QUOTES = ('USDT', 'USDC', 'USD', 'BTC', 'ETH', 'BNB')

_ex_cache = {}        # exchange_id -> ccxt instance
_resolved = {}        # input symbol -> (exchange_id, ccxt_symbol)


def _exchange(exid):
    if exid not in _ex_cache:
        _ex_cache[exid] = getattr(ccxt, exid)({'enableRateLimit': True})
    return _ex_cache[exid]


def _base(symbol: str) -> str:
    if '/' in symbol:
        return symbol.split('/')[0]
    for q in _QUOTES:
        if symbol.endswith(q):
            return symbol[:-len(q)]
    return symbol


def _resolve(symbol: str):
    """Find a reachable (exchange, symbol) for the requested pair. Cached after first hit."""
    if symbol in _resolved:
        return _resolved[symbol]
    base = _base(symbol)
    for exid in _CANDIDATES:
        try:
            ex = _exchange(exid)
            markets = ex.load_markets()
            for sym in (f"{base}/USDT", f"{base}/USD", f"{base}/USDC"):
                if sym in markets:
                    _resolved[symbol] = (exid, sym)
                    return _resolved[symbol]
        except Exception:
            continue  # try next exchange
    return (None, None)


def fetch_candles(symbol: str, timeframe: str = '1m', limit: int = 500):
    """Returns a list of [ms, open, high, low, close, volume]."""
    exid, sym = _resolve(symbol)
    if not exid:
        raise Exception(f"no reachable market data source for {symbol}")
    return _exchange(exid).fetch_ohlcv(sym, timeframe, limit=limit)


def fetch_last_price(symbol: str):
    exid, sym = _resolve(symbol)
    if not exid:
        return None
    try:
        return float(_exchange(exid).fetch_ticker(sym)['last'])
    except Exception:
        return None
