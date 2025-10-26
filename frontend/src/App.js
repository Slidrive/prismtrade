import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Strategies from './pages/Strategies';
import StrategyForm from './pages/StrategyForm';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (<AuthProvider><Router><Routes><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} /><Route path="/strategies" element={<PrivateRoute><Strategies /></PrivateRoute>} /><Route path="/strategies/new" element={<PrivateRoute><StrategyForm /></PrivateRoute>} /></Routes></Router></AuthProvider>);
}

export default App;
