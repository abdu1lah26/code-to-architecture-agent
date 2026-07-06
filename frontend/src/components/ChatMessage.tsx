import { QAMessage } from "../types";

interface ChatMessageProps {
  message: QAMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isQuestion = message.type === "question";

  return (
    <div
      className={`flex mb-4 ${isQuestion ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isQuestion
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-slate-100 text-slate-900 rounded-bl-none"
        }`}
      >
        <p className="text-sm">{message.content}</p>

        {/* Retrieved code chunks */}
        {!isQuestion && message.retrieved_chunks && message.retrieved_chunks.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold text-slate-700 border-t border-slate-300 pt-2">
              📚 Code References:
            </p>
            {message.retrieved_chunks.map((chunk, idx) => (
              <div
                key={idx}
                className="bg-white bg-opacity-90 rounded px-2 py-1 text-xs"
              >
                <p className="font-mono text-blue-600">{chunk.filename}</p>
                <p className="text-slate-600 truncate mt-1">{chunk.snippet}</p>
              </div>
            ))}
          </div>
        )}

        <p className="text-xs mt-2 opacity-70">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}