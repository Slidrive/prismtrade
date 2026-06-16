import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import TradingChart from '../components/TradingChart';
import { tradeAPI } from '../api/client';

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
const INTERVALS = ['1m', '5m', '15m', '1h', '4h', '1d'];

export default function Trade() {
  const { user, logout } = useAuth();
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('1m');
  const [price, setPrice] = useState(null);
  const [mode, setMode] = useState('demo');          // 'demo' | 'live'
  const [qty, setQty] = useState('0.01');
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);
  const [confirmLive, setConfirmLive] = useState(false);

  const handlePrice = useCallback((p) => setPrice(p), []);

  const placeOrder = async (side) => {
    if (mode === 'live' && !confirmLive) { setConfirmLive(true); return; }
    setBusy(true); setMsg(null);
    try {
      // Both modes hit the backend. mode='demo' -> paper balance (no API key);
      // mode='live' -> the user's connected exchange. The live mark price from the
      // chart is sent so paper fills happen at the real current price.
      const res = await tradeAPI.execute({ side, symbol, qty: parseFloat(qty), price, mode });
      const d = res.data || {};
      if (mode === 'live') {
        setMsg({ ok: true, text: `LIVE ${side.toUpperCase()} ${qty} ${symbol} @ ~${d.entry_price ?? d.exit_price ?? price} — ${d.order?.id ? `order ${d.order.id}` : 'submitted'}` });
      } else {
        const bal = d.paper_balance != null ? ` · paper balance $${Number(d.paper_balance).toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '';
        const pnl = d.profit_loss != null ? ` · P&L $${Number(d.profit_loss).toFixed(2)}` : '';
        setMsg({ ok: true, text: `DEMO ${side.toUpperCase()} ${qty} ${symbol} filled @ ${d.entry_price ?? d.exit_price ?? price}${pnl}${bal}` });
      }
    } catch (e) {
      setMsg({ ok: false, text: e.response?.data?.error || e.message || 'Order failed' });
    } finally {
      setBusy(false); setConfirmLive(false);
    }
  };

  const toggleAgent = async () => {
    // The autonomous agent worker (with risk limits + kill switch) is the next phase.
    // Not wired to a live loop yet — we don't fake something that can move real money.
    setMsg({
      ok: false,
      text: 'Autonomous agent is the next build phase (needs risk limits + kill switch before it can trade). Manual Demo/Live trading is live now.',
    });
  };

  const btn = (extra) => ({ padding: '0.6rem 1rem', border: '1px solid #00ff41', background: 'transparent', color: '#00ff41', cursor: 'pointer', borderRadius: 4, fontWeight: 'bold', ...extra });
  const liveTheme = mode === 'live' ? '#ff4444' : '#00ff41';

  return (
    <div style={{ minHeight: '100vh', background: '#0a0e27', color: '#00ff41' }}>
      <nav style={{ background: '#1a1f3a', padding: '1rem 2rem', borderBottom: '1px solid #00ff41', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>PRISM TRADE</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Link to="/" style={{ color: '#00ff41', textDecoration: 'none' }}>DASHBOARD</Link>
          <Link to="/strategies" style={{ color: '#00ff41', textDecoration: 'none' }}>STRATEGIES</Link>
          <Link to="/trading" style={{ color: '#00ff41', textDecoration: 'none', fontWeight: 'bold' }}>TRADING</Link>
          <span style={{ color: '#888' }}>{user?.username}</span>
          <button onClick={logout} style={btn()}>LOGOUT</button>
        </div>
      </nav>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '1rem', padding: '1rem', height: 'calc(100vh - 70px)' }}>
        {/* Chart panel */}
        <div style={{ background: '#1a1f3a', border: '1px solid #00ff41', borderRadius: 8, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ display: 'flex', gap: '0.5rem', padding: '0.75rem', borderBottom: '1px solid #2a2f4a', flexWrap: 'wrap' }}>
            <select value={symbol} onChange={e => setSymbol(e.target.value)} style={{ background: '#0a0e27', color: '#00ff41', border: '1px solid #00ff41', borderRadius: 4, padding: '0.4rem' }}>
              {SYMBOLS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <div style={{ display: 'flex', gap: 4 }}>
              {INTERVALS.map(tf => (
                <button key={tf} onClick={() => setInterval(tf)} style={btn({ padding: '0.4rem 0.7rem', background: interval === tf ? '#00ff41' : 'transparent', color: interval === tf ? '#0a0e27' : '#00ff41' })}>{tf}</button>
              ))}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <TradingChart symbol={symbol} interval={interval} onPrice={handlePrice} />
          </div>
        </div>

        {/* Order ticket */}
        <div style={{ background: '#1a1f3a', border: `1px solid ${liveTheme}`, borderRadius: 8, padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Demo / Live toggle */}
          <div style={{ display: 'flex', border: `1px solid ${liveTheme}`, borderRadius: 6, overflow: 'hidden' }}>
            {['demo', 'live'].map(m => (
              <button key={m} onClick={() => { setMode(m); setConfirmLive(false); }}
                style={{ flex: 1, padding: '0.6rem', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                  background: mode === m ? (m === 'live' ? '#ff4444' : '#00ff41') : 'transparent',
                  color: mode === m ? '#0a0e27' : (m === 'live' ? '#ff4444' : '#00ff41') }}>
                {m === 'live' ? '⚠ REAL MONEY' : 'DEMO'}
              </button>
            ))}
          </div>

          <div style={{ fontSize: '0.8rem', color: '#7d89b0' }}>
            {mode === 'live'
              ? 'Orders route to your connected exchange via your API key. Real funds at risk.'
              : 'Practice account. Live prices, simulated fills, no real funds.'}
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: '#888' }}>SYMBOL</label>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{symbol}</div>
          </div>
          <div>
            <label style={{ fontSize: '0.8rem', color: '#888' }}>MARK PRICE</label>
            <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#fff' }}>{price ? price.toLocaleString() : '—'}</div>
          </div>
          <div>
            <label style={{ fontSize: '0.8rem', color: '#888' }}>QUANTITY</label>
            <input value={qty} onChange={e => setQty(e.target.value)} type="number" step="0.001" min="0"
              style={{ width: '100%', background: '#0a0e27', color: '#00ff41', border: '1px solid #00ff41', borderRadius: 4, padding: '0.5rem', boxSizing: 'border-box' }} />
            <div style={{ fontSize: '0.8rem', color: '#7d89b0', marginTop: 4 }}>
              Est. notional: {price && qty ? `$${(price * parseFloat(qty || 0)).toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—'}
            </div>
          </div>

          {confirmLive && (
            <div style={{ background: '#3a1414', border: '1px solid #ff4444', borderRadius: 4, padding: '0.6rem', color: '#ff8888', fontSize: '0.85rem' }}>
              Confirm REAL-MONEY order. Click BUY/SELL again to submit.
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button disabled={busy || !price} onClick={() => placeOrder('buy')}
              style={btn({ flex: 1, background: '#00ff41', color: '#0a0e27', opacity: busy || !price ? 0.5 : 1 })}>BUY</button>
            <button disabled={busy || !price} onClick={() => placeOrder('sell')}
              style={btn({ flex: 1, background: '#ff4444', color: '#0a0e27', borderColor: '#ff4444', opacity: busy || !price ? 0.5 : 1 })}>SELL</button>
          </div>

          {/* Autonomous agent (next build phase) */}
          <div style={{ borderTop: '1px solid #2a2f4a', paddingTop: '1rem' }}>
            <button disabled={busy} onClick={toggleAgent}
              style={btn({ width: '100%', background: 'transparent', color: '#00ff41', opacity: busy ? 0.5 : 1 })}>
              ▶ DEPLOY TRADING AGENT
            </button>
            <div style={{ fontSize: '0.75rem', color: '#7d89b0', marginTop: 6 }}>
              Next phase: hands the {symbol} desk to an autonomous agent (with risk limits + kill switch) running your active strategy in {mode.toUpperCase()} mode.
            </div>
          </div>

          {msg && (
            <div style={{ fontSize: '0.85rem', color: msg.ok ? '#00ff41' : '#ff4444', wordBreak: 'break-word' }}>
              {msg.text}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
