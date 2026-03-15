import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin]   = useState(true);
  const [username, setUsername] = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  const handleSubmit = async () => {
    if (!username || !password) { setError("Username and password are required."); return; }
    if (!isLogin && !email)     { setError("Email is required for registration."); return; }
    try {
      setLoading(true); setError("");
      if (isLogin) await login(username, password);
      else         await register(username, email, password);
      navigate("/upload");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-4xl mb-2">🎓</div>
          <h1 className="text-2xl font-bold text-gray-800">AgenticLearn</h1>
          <p className="text-gray-500 text-sm mt-1">Adaptive Learning Platform</p>
        </div>
        <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
          <button onClick={() => { setIsLogin(true); setError(""); }}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all
              ${isLogin ? "bg-white shadow text-blue-600" : "text-gray-500"}`}>
            Login
          </button>
          <button onClick={() => { setIsLogin(false); setError(""); }}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all
              ${!isLogin ? "bg-white shadow text-blue-600" : "text-gray-500"}`}>
            Register
          </button>
        </div>
        <div className="space-y-4">
          <input type="text" placeholder="Username" value={username}
            onChange={e => setUsername(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
            className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {!isLogin && (
            <input type="email" placeholder="Email" value={email}
              onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
              className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          )}
          <input type="password" placeholder="Password" value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
            className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">{error}</div>
        )}
        <button onClick={handleSubmit} disabled={loading}
          className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-lg transition-all">
          {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
        </button>
      </div>
    </div>
  );
}