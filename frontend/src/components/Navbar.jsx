import { useNavigate, useLocation } from "react-router-dom";
import { logout } from "../services/api";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const token    = localStorage.getItem("token");
  const username = localStorage.getItem("username");

  if (!token) return null;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navLinks = [
    { path: "/upload",        label: "📄 Upload"   },
    { path: "/learning-path", label: "🗺️ My Path"  },
    { path: "/tutor",         label: "🤖 AI Tutor" },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/upload")}>
        <span className="text-xl">🎓</span>
        <span className="font-bold text-blue-600 text-lg">AgenticLearn</span>
      </div>
      <div className="flex items-center gap-1">
        {navLinks.map(link => (
          <button
            key={link.path}
            onClick={() => navigate(link.path)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${location.pathname === link.path
                ? "bg-blue-50 text-blue-600"
                : "text-gray-600 hover:bg-gray-100"}`}
          >
            {link.label}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">👤 {username}</span>
        <button onClick={handleLogout} className="text-sm text-red-500 hover:text-red-700 font-medium">
          Logout
        </button>
      </div>
    </nav>
  );
}