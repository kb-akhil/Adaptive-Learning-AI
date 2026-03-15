export default function QuestionCard({ question, index, selectedAnswer, onAnswer }) {
  return (
    <div className="bg-white rounded-xl shadow p-6 mb-4">
      {/* Topic + number */}
      <div className="flex items-center gap-2 mb-3">
        <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded-full">
          {question.topic}
        </span>
        <span className="text-xs text-gray-400">Q{index + 1}</span>
      </div>

      {/* Question text */}
      <p className="text-gray-800 font-medium mb-4 text-base leading-relaxed">
        {question.question}
      </p>

      {/* Options — each on its own line */}
      <div className="flex flex-col gap-2">
        {question.options.map(opt => {
          const isSelected = selectedAnswer === opt.key;
          return (
            <button
              key={opt.key}
              onClick={() => onAnswer(question.id, opt.key)}
              className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-all flex items-center gap-3
                ${isSelected
                  ? "border-blue-500 bg-blue-50 text-blue-700 font-medium"
                  : "border-gray-200 hover:border-blue-300 hover:bg-gray-50 text-gray-700"}`}
            >
              <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold flex-shrink-0
                ${isSelected ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-600"}`}>
                {opt.key}
              </span>
              <span>{opt.value}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}