import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { strategyAPI } from '../api/client';

export default function Strategies() {
  const [strategies, setStrategies] = useState([]);
  useEffect(() => { strategyAPI.getAll().then(r => setStrategies(r.data)).catch(console.error); }, []);
  return (<div style={{ minHeight: '100vh', background: '#0a0e27', color: '#00ff41', padding: '2rem' }}><h1>STRATEGIES</h1><Link to="/strategies/new" style={{ padding: '1rem', background: '#00ff41', color: '#0a0e27', textDecoration: 'none', fontWeight: 'bold', borderRadius: '4px' }}>+ CREATE</Link>{strategies.length === 0 ? <p>No strategies</p> : strategies.map(s => <div key={s.id} style={{ background: '#1a1f3a', padding: '1rem', margin: '1rem 0', borderRadius: '8px', border: '1px solid #00ff41' }}><h3>{s.name}</h3></div>)}</div>);
}
