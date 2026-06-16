import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { strategyAPI, backtestAPI } from '../api/client';

export default function StrategyForm() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [backtestResults, setBacktestResults] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', exchange: 'coinbase', trading_pair: 'BTC/USDT', timeframe: '1h', fast_ma: 10, slow_ma: 30, stop_loss_pct: 2, take_profit_pct: 5 });
  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
  const handleBacktest = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const strategyRes = await strategyAPI.create({ ...formData, strategy_type: 'ma_crossover', trading_mode: 'paper', parameters: { fast_ma: formData.fast_ma, slow_ma: formData.slow_ma } });
      const backtestRes = await backtestAPI.run(strategyRes.data.id, { days: 30, initial_capital: 10000 });
      setBacktestResults(backtestRes.data);
    } catch (err) { alert('Error: ' + (err.response?.data?.error || err.message)); }
    setLoading(false);
  };
  const s = { width: '100%', padding: '0.75rem', background: '#0a0e27', border: '1px solid #00ff41', color: '#00ff41', borderRadius: '4px' };
  return (<div style={{ minHeight: '100vh', background: '#0a0e27', color: '#00ff41', padding: '2rem' }}><div style={{ maxWidth: '1200px', margin: '0 auto' }}><h1>CREATE STRATEGY</h1><div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}><div style={{ background: '#1a1f3a', padding: '2rem', borderRadius: '8px', border: '1px solid #00ff41' }}><form onSubmit={handleBacktest}>
<div style={{ marginBottom: '1rem' }}><label style={{ display: 'block', marginBottom: '0.5rem' }}>Strategy Name</label><input name="name" value={formData.name} onChange={handleChange} style={s} required /></div>
<div style={{ marginBottom: '1rem' }}><label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label><textarea name="description" value={formData.description} onChange={handleChange} style={{...s, minHeight: '60px'}} /></div>
<div style={{ marginBottom: '1rem' }}><label style={{ display: 'block', marginBottom: '0.5rem' }}>Trading Pair</label><input name="trading_pair" value={formData.trading_pair} onChange={handleChange} style={s} /></div>
<div style={{ marginBottom: '1rem' }}><label style={{ display: 'block', marginBottom: '0.5rem' }}>Timeframe</label><select name="timeframe" value={formData.timeframe} onChange={handleChange} style={s}><option value="1m">1 Minute</option><option value="5m">5 Minutes</option><option value="1h">1 Hour</option><option value="1d">1 Day</option></select></div>
<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}><div><label style={{ display: 'block', marginBottom: '0.5rem' }}>Fast MA</label><input type="number" name="fast_ma" value={formData.fast_ma} onChange={handleChange} style={s} /></div><div><label style={{ display: 'block', marginBottom: '0.5rem' }}>Slow MA</label><input type="number" name="slow_ma" value={formData.slow_ma} onChange={handleChange} style={s} /></div></div>
<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}><div><label style={{ display: 'block', marginBottom: '0.5rem' }}>Stop Loss %</label><input type="number" step="0.1" name="stop_loss_pct" value={formData.stop_loss_pct} onChange={handleChange} style={s} /></div><div><label style={{ display: 'block', marginBottom: '0.5rem' }}>Take Profit %</label><input type="number" step="0.1" name="take_profit_pct" value={formData.take_profit_pct} onChange={handleChange} style={s} /></div></div>
<button type="submit" disabled={loading} style={{ width: '100%', padding: '1rem', background: '#00ff41', border: 'none', color: '#0a0e27', fontWeight: 'bold', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer' }}>{loading ? 'RUNNING BACKTEST...' : 'RUN BACKTEST'}</button></form></div>
<div style={{ background: '#1a1f3a', padding: '2rem', borderRadius: '8px', border: '1px solid #00ff41' }}><h2 style={{ marginTop: 0 }}>BACKTEST RESULTS</h2>{!backtestResults ? (<p style={{ color: '#888' }}>Run a backtest to see results</p>) : (<div><div style={{ background: '#0a0e27', padding: '1rem', borderRadius: '4px', marginBottom: '1rem' }}><div style={{ fontSize: '0.75rem', color: '#888' }}>TOTAL RETURN</div><div style={{ fontSize: '2rem', fontWeight: 'bold', color: backtestResults.total_return_pct >= 0 ? '#00ff41' : '#ff4444' }}>{backtestResults.total_return_pct?.toFixed(2)}%</div></div>
<div style={{ marginBottom: '0.5rem' }}>Win Rate: {backtestResults.win_rate?.toFixed(1)}%</div>
<div style={{ marginBottom: '0.5rem' }}>Total Trades: {backtestResults.total_trades}</div>
<div style={{ marginBottom: '0.5rem' }}>Profit Factor: {backtestResults.profit_factor?.toFixed(2)}</div>
<div style={{ marginBottom: '1rem' }}>Max Drawdown: {backtestResults.max_drawdown_pct?.toFixed(2)}%</div>
<button onClick={() => navigate('/strategies')} style={{ width: '100%', padding: '1rem', background: '#00ff41', border: 'none', color: '#0a0e27', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>SAVE STRATEGY</button></div>)}</div></div></div></div>);}
