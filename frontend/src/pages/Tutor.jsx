import { useState, useRef, useEffect } from "react";
import { askTutor } from "../services/api";

function RenderAnswer({ text }) {
  const lines = text.split("\n");
  return (
    <div className="space-y-1.5">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} className="h-1" />;

        if (/^[-*]\s+/.test(trimmed)) {
          const content = trimmed.replace(/^[-*]\s+/, "");
          return (
            <div key={i} className="flex items-start gap-2">
              <span className="mt-2 w-1.5 h-1.5 rounded-full bg-purple-400 flex-shrink-0" />
              <span className="text-sm leading-relaxed">{renderInline(content)}</span>
            </div>
          );
        }

        const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
        if (numMatch) {
          return (
            <div key={i} className="flex items-start gap-2">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-purple-100 text-purple-700 text-xs font-bold flex items-center justify-center mt-0.5">
                {numMatch[1]}
              </span>
              <span className="text-sm leading-relaxed">{renderInline(numMatch[2])}</span>
            </div>
          );
        }

        if (/^#{1,3}\s+/.test(trimmed)) {
          return <p key={i} className="text-sm font-bold text-gray-800 mt-2">{trimmed.replace(/^#{1,3}\s+/, "")}</p>;
        }

        return <p key={i} className="text-sm leading-relaxed">{renderInline(trimmed)}</p>;
      })}
    </div>
  );
}

function renderInline(text) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1
      ? <strong key={i} className="font-semibold text-gray-900">{part}</strong>
      : part
  );
}

export default function Tutor() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I'm your AI Tutor 🤖 Ask me anything about your Computer Networks topics and I'll explain it simply." }
  ]);
  const [input, setInput]     = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef             = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;

    const newMessages = [...messages, { role: "user", text: q }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      // Send full chat history for context
      const history = newMessages.slice(1); // skip initial greeting
      const data = await askTutor(q, "", history);
      setMessages(prev => [...prev, { role: "assistant", text: data.answer }]);
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        text: "Sorry, I'm having trouble connecting. Please try again.",
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="text-xl font-bold text-gray-800">🤖 AI Tutor</h1>
        <p className="text-gray-500 text-sm">Powered by Cohere · Ask anything about your topics</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl w-full mx-auto">
        {messages.map((msg, i) => (
          <div key={i} className={`flex mb-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3 mt-1 flex-shrink-0 text-base">🤖</div>
            )}
            <div className={`max-w-xl px-4 py-3 rounded-2xl
              ${msg.role === "user"
                ? "bg-blue-600 text-white rounded-br-sm text-sm leading-relaxed"
                : msg.isError
                  ? "bg-red-50 text-red-700 border border-red-200 text-sm"
                  : "bg-white text-gray-800 shadow border border-gray-100 rounded-bl-sm"}`}>
              {msg.role === "assistant" && !msg.isError
                ? <RenderAnswer text={msg.text} />
                : msg.text}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center ml-3 mt-1 flex-shrink-0 text-base">👤</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start mb-4">
            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3 flex-shrink-0 text-base">🤖</div>
            <div className="bg-white shadow border border-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm">
              <div className="flex gap-1 items-center">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            placeholder="Ask about any topic from your syllabus..."
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white px-5 py-3 rounded-xl font-medium transition-all"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}