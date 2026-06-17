import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { strategyAPI, tradeAPI } from '../api/client';
import NavBar from '../components/NavBar';

export default function Dashboard() {
  const [strategies, setStrategies] = useState([]);
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState({ total_pnl: 0, win_rate: 0, total_trades: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [stratRes, tradeRes] = await Promise.all([strategyAPI.getAll(), tradeAPI.getAll({ limit: 10 })]);
      // Endpoints may return a bare array or { trades: [...] } / { strategies: [...] }.
      const strats = Array.isArray(stratRes.data) ? stratRes.data : (stratRes.data?.strategies || []);
      const trs = Array.isArray(tradeRes.data) ? tradeRes.data : (tradeRes.data?.trades || []);
      setStrategies(strats);
      setTrades(trs);
      calculateStats(trs);
    } catch (err) {
      console.error('Error loading data:', err);
      setStrategies([]);
      setTrades([]);
    }
  };

  const calculateStats = (trades) => {
    const list = Array.isArray(trades) ? trades : [];
    const pnlOf = (t) => (t.profit_loss ?? t.pnl ?? 0);
    const total = list.length;
    const winners = list.filter(t => pnlOf(t) > 0).length;
    const pnl = list.reduce((sum, t) => sum + pnlOf(t), 0);
    setStats({ total_pnl: pnl, win_rate: total ? (winners / total) * 100 : 0, total_trades: total });
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0a0e27', color: '#00ff41' }}>
      <NavBar />
      <div style={{ padding: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ background: '#1a1f3a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #00ff41' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>TOTAL P&L</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: stats.total_pnl >= 0 ? '#00ff41' : '#ff4444' }}>${stats.total_pnl.toFixed(2)}</div>
          </div>
          <div style={{ background: '#1a1f3a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #00ff41' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>WIN RATE</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.win_rate.toFixed(1)}%</div>
          </div>
          <div style={{ background: '#1a1f3a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #00ff41' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>TOTAL TRADES</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total_trades}</div>
          </div>
        </div>
        <div style={{ background: '#1a1f3a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #00ff41', marginBottom: '2rem' }}>
          <h2 style={{ marginTop: 0 }}>ACTIVE STRATEGIES</h2>
          {strategies.length === 0 ? (
            <p style={{ color: '#888' }}>No strategies yet. <Link to="/strategies" style={{ color: '#00ff41' }}>Create one</Link></p>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {strategies.slice(0, 5).map(s => (
                <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', background: '#0a0e27', borderRadius: '4px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{s.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#888' }}>{s.exchange} - {s.trading_pair}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.875rem', color: '#888' }}>Status</div>
                    <div style={{ color: s.status === 'active' ? '#00ff41' : '#888' }}>{s.status.toUpperCase()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={{ background: '#1a1f3a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #00ff41' }}>
          <h2 style={{ marginTop: 0 }}>RECENT TRADES</h2>
          {trades.length === 0 ? (
            <p style={{ color: '#888' }}>No trades yet. <Link to="/trading" style={{ color: '#00ff41' }}>Start trading</Link></p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #00ff41' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>TIME</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>PAIR</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>SIDE</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>P&L</th>
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 10).map((t, i) => {
                  const pnl = t.profit_loss ?? t.pnl ?? 0;
                  return (
                  <tr key={t.trade_id ?? t.id ?? i} style={{ borderBottom: '1px solid #2a2f4a' }}>
                    <td style={{ padding: '0.75rem' }}>{t.entry_time ? new Date(t.entry_time).toLocaleString() : '—'}</td>
                    <td style={{ padding: '0.75rem' }}>{t.symbol}</td>
                    <td style={{ padding: '0.75rem', color: t.side === 'buy' ? '#00ff41' : '#ff4444' }}>{(t.side || '').toUpperCase()}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', color: pnl >= 0 ? '#00ff41' : '#ff4444' }}>${Number(pnl).toFixed(2)}</td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
