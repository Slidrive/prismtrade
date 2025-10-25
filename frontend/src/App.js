import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState("");
  const [backtestResult, setBacktestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_URL = "http://127.0.0.1:8000";

  const handleSignup = async () => {
    try {
      const response = await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        alert("Signup successful! Please login.");
        setIsSignup(false);
        setUsername("");
        setEmail("");
        setPassword("");
      } else {
        alert("Signup failed: " + data.detail);
      }
    } catch (error) {
      alert("Error: " + error.message);
    }
  };

  const handleLogin = async () => {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        setIsLoggedIn(true);
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", username);
        fetchStrategies(data.access_token);
      } else {
        alert("Login failed: " + data.detail);
      }
    } catch (error) {
      alert("Error: " + error.message);
    }
  };

  const fetchStrategies = async (tok) => {
    try {
      const response = await fetch(`${API_URL}/strategies`, {
        headers: { Authorization: `Bearer ${tok}` },
      });
      const data = await response.json();
      setStrategies(data.strategies.split("\n").filter((s) => s.trim()));
    } catch (error) {
      console.error("Failed to fetch strategies:", error);
    }
  };

  const runBacktest = async () => {
    if (!selectedStrategy) {
      alert("Please select a strategy");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/backtest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          strategy: selectedStrategy,
          timerange: "20240901-20241025",
        }),
      });
      const data = await response.json();
      setBacktestResult(data);
    } catch (error) {
      alert("Backtest failed: " + error.message);
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setToken(null);
    setUsername("");
    setPassword("");
    localStorage.removeItem("token");
    localStorage.removeItem("username");
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUsername = localStorage.getItem("username");
    if (savedToken) {
      setToken(savedToken);
      setIsLoggedIn(true);
      setUsername(savedUsername);
      fetchStrategies(savedToken);
    }
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Trading Platform</h1>
        {isLoggedIn && <p>Welcome, {username}!</p>}
      </header>

      {!isLoggedIn ? (
        <div className="auth-container">
          <h2>{isSignup ? "Sign Up" : "Login"}</h2>
          {isSignup && (
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          )}
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={isSignup ? handleSignup : handleLogin}>
            {isSignup ? "Sign Up" : "Login"}
          </button>
          <button onClick={() => setIsSignup(!isSignup)}>
            {isSignup ? "Back to Login" : "Create Account"}
          </button>
        </div>
      ) : (
        <div className="container">
          <section className="strategies">
            <h2>Available Strategies</h2>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
            >
              <option value="">-- Select a strategy --</option>
              {strategies.map((strategy, idx) => (
                <option key={idx} value={strategy}>
                  {strategy}
                </option>
              ))}
            </select>
            <button onClick={runBacktest} disabled={loading}>
              {loading ? "Running Backtest..." : "Run Backtest"}
            </button>
            <button onClick={handleLogout}>Logout</button>
          </section>

          {backtestResult && (
            <section className="results">
              <h2>Backtest Results</h2>
              <pre>{JSON.stringify(backtestResult, null, 2)}</pre>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

export default App;