import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Shared top navigation so every page can get back to the others.
export default function NavBar() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  const link = (to, label) => (
    <Link to={to} style={{ color: '#00ff41', textDecoration: 'none', fontWeight: pathname === to ? 'bold' : 'normal' }}>{label}</Link>
  );
  return (
    <nav style={{ background: '#1a1f3a', padding: '1rem 2rem', borderBottom: '1px solid #00ff41', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Link to="/" style={{ color: '#00ff41', textDecoration: 'none' }}><h1 style={{ margin: 0 }}>PRISM TRADE</h1></Link>
      <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
        {link('/', 'DASHBOARD')}
        {link('/strategies', 'STRATEGIES')}
        {link('/trading', 'TRADING')}
        {user?.username && <span style={{ color: '#888' }}>{user.username}</span>}
        <button onClick={logout} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid #00ff41', color: '#00ff41', cursor: 'pointer', borderRadius: '4px' }}>LOGOUT</button>
      </div>
    </nav>
  );
}
