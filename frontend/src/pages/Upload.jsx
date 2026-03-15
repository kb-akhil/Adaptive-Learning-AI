import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { uploadSyllabus, getSyllabi } from "../services/api";

export default function Upload() {
  const navigate  = useNavigate();
  const fileRef   = useRef(null);
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError]         = useState("");
  const [syllabi, setSyllabi]     = useState([]);

  useEffect(() => {
    getSyllabi().then(setSyllabi).catch(() => {});
  }, []);

  const handleUpload = async () => {
    if (!file) { setError("Please select a PDF file."); return; }
    if (!file.name.endsWith(".pdf")) { setError("Only PDF files accepted."); return; }
    try {
      setUploading(true); setError("");
      const data = await uploadSyllabus(file);
      navigate(`/assessment/${data.syllabus_id}`);
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow p-8 mb-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-1">📄 Upload Syllabus</h1>
          <p className="text-gray-500 text-sm mb-6">Upload a PDF to generate your personalized assessment</p>
          <div onClick={() => fileRef.current.click()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
              ${file ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"}`}>
            <div className="text-4xl mb-3">{file ? "✅" : "📁"}</div>
            {file
              ? <p className="text-blue-700 font-medium">{file.name}</p>
              : <><p className="text-gray-600 font-medium">Click to select PDF</p>
                  <p className="text-gray-400 text-sm mt-1">Only .pdf files accepted</p></>
            }
            <input ref={fileRef} type="file" accept=".pdf" className="hidden"
              onChange={e => { setFile(e.target.files[0]); setError(""); }} />
          </div>
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">{error}</div>
          )}
          <button onClick={handleUpload} disabled={uploading || !file}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 rounded-xl transition-all">
            {uploading ? "Uploading & Extracting Topics..." : "Upload & Start Assessment"}
          </button>
        </div>

        {syllabi.length > 0 && (
          <div className="bg-white rounded-2xl shadow p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4">📚 Previous Uploads</h2>
            <div className="space-y-3">
              {syllabi.map(s => (
                <div key={s.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{s.filename}</p>
                    <p className="text-xs text-gray-400">{s.subject} · {new Date(s.uploaded_at).toLocaleDateString()}</p>
                  </div>
                  <button onClick={() => navigate(`/assessment/${s.id}`)}
                    className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                    Assess Again
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}