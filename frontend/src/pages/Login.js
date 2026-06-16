import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0e27' }}>
      <div style={{ background: '#1a1f3a', padding: '2rem', borderRadius: '8px', width: '400px', border: '1px solid #00ff41' }}>
        <h2 style={{ color: '#00ff41', marginBottom: '1.5rem', textAlign: 'center' }}>PRISM TRADE</h2>
        <form onSubmit={handleSubmit}>
          {error && <div style={{ color: '#ff4444', marginBottom: '1rem' }}>{error}</div>}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ color: '#00ff41', display: 'block', marginBottom: '0.5rem' }}>Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: '100%', padding: '0.75rem', background: '#0a0e27', border: '1px solid #00ff41', color: '#00ff41', borderRadius: '4px' }} required />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ color: '#00ff41', display: 'block', marginBottom: '0.5rem' }}>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: '100%', padding: '0.75rem', background: '#0a0e27', border: '1px solid #00ff41', color: '#00ff41', borderRadius: '4px' }} required />
          </div>
          <button type="submit" style={{ width: '100%', padding: '0.75rem', background: '#00ff41', border: 'none', color: '#0a0e27', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>LOGIN</button>
        </form>
        <p style={{ color: '#888', textAlign: 'center', marginTop: '1rem' }}>No account? <Link to="/register" style={{ color: '#00ff41' }}>Register</Link></p>
      </div>
    </div>
  );
}
