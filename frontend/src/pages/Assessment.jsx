import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { generateAssessment, submitAssessment } from "../services/api";
import QuestionCard from "../components/QuestionCard";

export default function Assessment() {
  const { syllabusId } = useParams();
  const navigate       = useNavigate();

  // Prevent ANY double calls — StrictMode, re-renders, etc.
  const hasFetched = useRef(false);

  const [questions, setQuestions]       = useState([]);
  const [assessmentId, setAssessmentId] = useState(null);
  const [answers, setAnswers]           = useState({});
  const [loading, setLoading]           = useState(true);
  const [submitting, setSubmitting]     = useState(false);
  const [error, setError]               = useState("");

  useEffect(() => {
    // Hard guard — only ever run once per mount
    if (hasFetched.current) return;
    hasFetched.current = true;

    console.log("[Assessment] Generating for syllabus:", syllabusId);

    generateAssessment(syllabusId)
      .then(data => {
        setQuestions(data.questions || []);
        setAssessmentId(data.assessment_id);
      })
      .catch(err => setError(err.message || "Failed to generate assessment."))
      .finally(() => setLoading(false));
  }, [syllabusId]);

  const handleAnswer = (questionId, selectedKey) => {
    setAnswers(prev => ({ ...prev, [String(questionId)]: selectedKey }));
  };

  const handleSubmit = async () => {
    const unanswered = questions.filter(q => !answers[String(q.id)]);
    if (unanswered.length > 0) {
      setError(`Please answer all questions. ${unanswered.length} remaining.`);
      return;
    }
    try {
      setSubmitting(true);
      setError("");
      await submitAssessment(assessmentId, answers);
      navigate("/learning-path");
    } catch (err) {
      setError(err.message || "Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const answeredCount = Object.keys(answers).length;
  const progress = questions.length > 0
    ? Math.round((answeredCount / questions.length) * 100)
    : 0;

  // ── Loading ──────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p className="text-gray-600 text-lg font-medium">Generating your assessment...</p>
        <p className="text-gray-400 text-sm mt-2">This may take 10–20 seconds</p>
      </div>
    </div>
  );

  // ── Error (no questions) ─────────────────────────────────
  if (error && questions.length === 0) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow p-8 max-w-md text-center">
        <div className="text-5xl mb-4">⚠️</div>
        <h2 className="text-xl font-bold text-gray-800 mb-2">Assessment Error</h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <button
          onClick={() => navigate("/upload")}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Back to Upload
        </button>
      </div>
    </div>
  );

  // ── Assessment ───────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-1">📝 Assessment</h1>
          <p className="text-gray-500 text-sm mb-4">
            {questions.length} questions · Answer all to submit
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 text-right">
            {answeredCount} / {questions.length} answered
          </p>
        </div>

        {/* Questions */}
        {questions.map((q, idx) => (
          <QuestionCard
            key={q.id}
            question={q}
            index={idx}
            selectedAnswer={answers[String(q.id)]}
            onAnswer={handleAnswer}
          />
        ))}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-4">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="bg-white rounded-xl shadow p-6 mt-4">
          <button
            onClick={handleSubmit}
            disabled={submitting || answeredCount < questions.length}
            className={`w-full py-3 rounded-lg font-semibold text-white transition-all
              ${answeredCount === questions.length && !submitting
                ? "bg-green-600 hover:bg-green-700"
                : "bg-gray-300 cursor-not-allowed"}`}
          >
            {submitting
              ? "Submitting..."
              : `Submit Assessment (${answeredCount}/${questions.length})`}
          </button>
        </div>

      </div>
    </div>
  );
}