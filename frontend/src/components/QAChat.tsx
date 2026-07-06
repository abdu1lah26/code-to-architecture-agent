import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "./ChatMessage";
import { useQA } from "../hooks/useQA";

interface QAChatProps {
  jobId: string;
  docsId: string;
}

export function QAChat({ jobId, docsId }: QAChatProps) {
  const [question, setQuestion] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, loading, error, askQuestion } = useQA();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim()) return;

    const currentQuestion = question;
    setQuestion("");

    try {
      await askQuestion(jobId, currentQuestion);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
      <h3 className="text-lg font-bold text-slate-900 mb-4">
        🤖 Ask About Architecture
      </h3>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto mb-4 p-4 bg-slate-50 rounded-lg">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-500 text-sm">
              💬 Ask questions about how this codebase is structured, what patterns it uses, or how specific features work.
            </p>
            <div className="mt-4 space-y-2 text-left inline-block">
              <p className="text-xs text-slate-600 font-medium">Example questions:</p>
              <ul className="text-xs text-slate-600 space-y-1">
                <li>• "How does authentication work?"</li>
                <li>• "What design patterns are used?"</li>
                <li>• "What are the main services?"</li>
              </ul>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-red-800 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the architecture..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          {loading ? "..." : "Send"}
        </button>
      </form>

      {/* Info */}
      <p className="text-xs text-slate-500 mt-3">
        💡 Answers are grounded in actual code from your repository
      </p>
    </div>
  );
}