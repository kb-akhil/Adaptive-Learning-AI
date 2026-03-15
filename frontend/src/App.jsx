import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import Assessment from "./pages/Assessment";
import LearningPath from "./pages/LearningPath";
import Tutor from "./pages/Tutor";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/login"                    element={<Login />} />
        <Route path="/upload"                   element={<PrivateRoute><Upload /></PrivateRoute>} />
        <Route path="/assessment/:syllabusId"   element={<PrivateRoute><Assessment /></PrivateRoute>} />
        <Route path="/learning-path"            element={<PrivateRoute><LearningPath /></PrivateRoute>} />
        <Route path="/tutor"                    element={<PrivateRoute><Tutor /></PrivateRoute>} />

        {/* Always land on /upload — never auto-resume assessment */}
        <Route path="/"   element={<Navigate to="/upload" replace />} />
        <Route path="*"   element={<Navigate to="/upload" replace />} />
      </Routes>
    </BrowserRouter>
  );
}