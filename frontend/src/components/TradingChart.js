import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';

/**
 * Live candlestick chart (TradingView Lightweight Charts, Apache-2.0).
 *
 * Data comes from OUR backend (/api/market/candles), which fetches public OHLCV
 * server-side from Binance.US. This avoids the browser CORS / US geo-block you get
 * calling api.binance.com directly. History loads once, then we poll for updates.
 */
const POLL_MS = 3000;

export default function TradingChart({ symbol = 'BTCUSDT', interval = '1m', onPrice }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const [status, setStatus] = useState('connecting');
  const [last, setLast] = useState(null);

  // Build the chart once.
  useEffect(() => {
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: '#0a0e27' }, textColor: '#7d89b0' },
      grid: {
        vertLines: { color: 'rgba(0,255,65,0.05)' },
        horzLines: { color: 'rgba(0,255,65,0.05)' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: 'rgba(0,255,65,0.2)' },
      timeScale: { borderColor: 'rgba(0,255,65,0.2)', timeVisible: true, secondsVisible: false },
    });
    const candles = chart.addCandlestickSeries({
      upColor: '#00ff41', downColor: '#ff4444',
      borderUpColor: '#00ff41', borderDownColor: '#ff4444',
      wickUpColor: '#00ff41', wickDownColor: '#ff4444',
    });
    const volume = chart.addHistogramSeries({
      priceFormat: { type: 'volume' }, priceScaleId: '', color: 'rgba(0,255,65,0.3)',
    });
    volume.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });

    chartRef.current = chart;
    candleSeriesRef.current = candles;
    volumeSeriesRef.current = volume;
    return () => { chart.remove(); chartRef.current = null; };
  }, []);

  // Load history + poll for live updates whenever symbol/interval changes.
  useEffect(() => {
    let cancelled = false;
    let timer = null;
    setStatus('connecting');

    const url = (limit) => `/api/market/candles?symbol=${symbol}&interval=${interval}&limit=${limit}`;
    const toCandle = (k) => ({ time: k[0] / 1000, open: +k[1], high: +k[2], low: +k[3], close: +k[4] });
    const toVol = (k) => ({ time: k[0] / 1000, value: +k[5], color: +k[4] >= +k[1] ? 'rgba(0,255,65,0.3)' : 'rgba(255,68,68,0.3)' });

    async function loadHistory() {
      try {
        const res = await fetch(url(500));
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const raw = await res.json();
        if (cancelled || !Array.isArray(raw) || !raw.length) {
          if (!cancelled) setStatus('error');
          return;
        }
        candleSeriesRef.current?.setData(raw.map(toCandle));
        volumeSeriesRef.current?.setData(raw.map(toVol));
        const c = +raw[raw.length - 1][4];
        setLast(c); onPrice?.(c); setStatus('live');
      } catch (e) {
        if (!cancelled) setStatus('error');
      }
    }

    async function poll() {
      try {
        const res = await fetch(url(2));
        if (!res.ok) return;
        const raw = await res.json();
        if (cancelled || !Array.isArray(raw) || !raw.length) return;
        raw.forEach(k => { candleSeriesRef.current?.update(toCandle(k)); volumeSeriesRef.current?.update(toVol(k)); });
        const c = +raw[raw.length - 1][4];
        setLast(c); onPrice?.(c); setStatus('live');
      } catch (e) { /* transient; keep polling */ }
    }

    loadHistory().then(() => { if (!cancelled) timer = setInterval(poll, POLL_MS); });
    return () => { cancelled = true; if (timer) clearInterval(timer); };
  }, [symbol, interval, onPrice]);

  const statusColor = { live: '#00ff41', connecting: '#ffaa00', error: '#ff4444' }[status] || '#ffaa00';

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div style={{ position: 'absolute', top: 8, left: 12, zIndex: 5, fontFamily: 'monospace', pointerEvents: 'none' }}>
        <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '1.1rem' }}>{symbol}</span>
        <span style={{ color: '#7d89b0', marginLeft: 8 }}>{interval}</span>
        {last != null && <span style={{ color: '#00ff41', marginLeft: 12, fontSize: '1.1rem' }}>{last.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>}
        <span style={{ color: statusColor, marginLeft: 12, fontSize: '0.75rem' }}>● {status.toUpperCase()}</span>
      </div>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
