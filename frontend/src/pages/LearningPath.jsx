import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getLatestLearningPath } from "../services/api";
import ModuleCard from "../components/ModuleCard";

export default function LearningPath() {
  const navigate = useNavigate();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    getLatestLearningPath()
      .then(setData)
      .catch(err => setError(err.message || "No learning path found."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p className="text-gray-500">Loading your learning path...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow p-8 max-w-md text-center">
        <div className="text-5xl mb-4">📭</div>
        <h2 className="text-xl font-bold text-gray-800 mb-2">No Learning Path Yet</h2>
        <p className="text-gray-500 mb-6">Complete an assessment first to generate your personalized learning path.</p>
        <button onClick={() => navigate("/upload")} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
          Upload Syllabus
        </button>
      </div>
    </div>
  );

  const path    = data?.learning_path || {};
  const modules = path?.modules || [];

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">🗺️ Your Learning Path</h1>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-blue-600">{Math.round(data.accuracy || 0)}%</p>
              <p className="text-xs text-gray-500 mt-1">Assessment Score</p>
            </div>
            <div className="bg-purple-50 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-purple-600">{path.total_modules || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Total Modules</p>
            </div>
            <div className="bg-green-50 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{path.total_estimated_hours || 0}h</p>
              <p className="text-xs text-gray-500 mt-1">Estimated Time</p>
            </div>
          </div>
          {path.recommendation && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
              <p className="text-amber-800 text-sm">💡 {path.recommendation}</p>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            {data.weak_topics?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-red-500 uppercase mb-2">⚠️ Needs Work</p>
                <div className="flex flex-wrap gap-1">
                  {data.weak_topics.map(t => (
                    <span key={t} className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full">{t}</span>
                  ))}
                </div>
              </div>
            )}
            {data.strong_topics?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-green-500 uppercase mb-2">✅ Strong</p>
                <div className="flex flex-wrap gap-1">
                  {data.strong_topics.map(t => (
                    <span key={t} className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">{t}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-700">📚 Study Modules</h2>
          <div className="flex gap-3 text-xs text-gray-500">
            <span>🔴 High Priority</span><span>🟡 Medium</span><span>🟢 Review</span>
          </div>
        </div>

        {modules.map(m => <ModuleCard key={m.module_number} module={m} />)}

        <div className="mt-6 text-center">
          <button onClick={() => navigate("/tutor")}
            className="bg-purple-600 text-white px-8 py-3 rounded-xl hover:bg-purple-700 font-semibold">
            🤖 Ask AI Tutor for Help
          </button>
        </div>
      </div>
    </div>
  );
}