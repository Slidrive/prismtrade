import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';

/**
 * Real live candlestick chart powered by TradingView Lightweight Charts (Apache-2.0).
 * Data is LIVE from Binance public market data — no API key, real ticks:
 *   - REST  https://api.binance.com/api/v3/klines  (historical candles)
 *   - WS    wss://stream.binance.com:9443/ws/<symbol>@kline_<interval>  (live updates)
 *
 * This is market data only. It is independent of which account (demo/live)
 * an order is routed to — flip the toggle in the order ticket for that.
 */
const BINANCE_REST = 'https://api.binance.com/api/v3/klines';
const BINANCE_WS = 'wss://stream.binance.com:9443/ws';

export default function TradingChart({ symbol = 'BTCUSDT', interval = '1m', onPrice }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const wsRef = useRef(null);
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
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      color: 'rgba(0,255,65,0.3)',
    });
    volume.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });

    chartRef.current = chart;
    candleSeriesRef.current = candles;
    volumeSeriesRef.current = volume;

    return () => { chart.remove(); chartRef.current = null; };
  }, []);

  // Load history + open a live websocket whenever symbol/interval changes.
  useEffect(() => {
    let cancelled = false;
    setStatus('connecting');

    async function loadHistory() {
      const url = `${BINANCE_REST}?symbol=${symbol}&interval=${interval}&limit=500`;
      const res = await fetch(url);
      const raw = await res.json();
      if (cancelled || !Array.isArray(raw)) return;

      const candleData = raw.map(k => ({
        time: k[0] / 1000,
        open: +k[1], high: +k[2], low: +k[3], close: +k[4],
      }));
      const volData = raw.map(k => ({
        time: k[0] / 1000,
        value: +k[5],
        color: +k[4] >= +k[1] ? 'rgba(0,255,65,0.3)' : 'rgba(255,68,68,0.3)',
      }));

      candleSeriesRef.current?.setData(candleData);
      volumeSeriesRef.current?.setData(volData);
      const lastClose = candleData[candleData.length - 1]?.close;
      if (lastClose) { setLast(lastClose); onPrice?.(lastClose); }
    }

    function openSocket() {
      const stream = `${symbol.toLowerCase()}@kline_${interval}`;
      const ws = new WebSocket(`${BINANCE_WS}/${stream}`);
      wsRef.current = ws;

      ws.onopen = () => !cancelled && setStatus('live');
      ws.onclose = () => !cancelled && setStatus('disconnected');
      ws.onerror = () => !cancelled && setStatus('error');
      ws.onmessage = (evt) => {
        const k = JSON.parse(evt.data).k;
        if (!k) return;
        const bar = { time: k.t / 1000, open: +k.o, high: +k.h, low: +k.l, close: +k.c };
        candleSeriesRef.current?.update(bar);
        volumeSeriesRef.current?.update({
          time: k.t / 1000, value: +k.v,
          color: +k.c >= +k.o ? 'rgba(0,255,65,0.3)' : 'rgba(255,68,68,0.3)',
        });
        setLast(+k.c);
        onPrice?.(+k.c);
      };
    }

    loadHistory().then(() => { if (!cancelled) openSocket(); });

    return () => {
      cancelled = true;
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [symbol, interval, onPrice]);

  const statusColor = { live: '#00ff41', connecting: '#ffaa00', disconnected: '#ff4444', error: '#ff4444' }[status];

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
