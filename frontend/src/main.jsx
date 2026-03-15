import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

// StrictMode removed — it causes double useEffect calls in dev
// which triggers the model to load and generate twice
createRoot(document.getElementById("root")).render(<App />);