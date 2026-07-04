import { DocsResponse } from "../types";
import { downloadAsMarkdown } from "../utils/markdown";
import { useState } from "react";

interface DocsViewerProps {
  docs: DocsResponse;
  onNewAnalysis: () => void;
}

export function DocsViewer({ docs, onNewAnalysis }: DocsViewerProps) {
  const [viewMode, setViewMode] = useState<"markdown" | "diagram">("markdown");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(docs.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    downloadAsMarkdown(docs.markdown, "architecture.md");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-green-900 mb-2">✅ Analysis Complete!</h2>
        <p className="text-green-700">
          Your architecture documentation has been generated below.
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          {/* View mode toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode("markdown")}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                viewMode === "markdown"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-200 text-slate-700 hover:bg-slate-300"
              }`}
            >
              📄 Markdown
            </button>
            {docs.mermaid_diagram && (
              <button
                onClick={() => setViewMode("diagram")}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === "diagram"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
              >
                🔗 Diagram
              </button>
            )}
          </div>

          <div className="flex-1"></div>

          {/* Action buttons */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={handleCopy}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-medium transition text-sm"
            >
              {copied ? "✓ Copied" : "📋 Copy"}
            </button>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-medium transition text-sm"
            >
              💾 Download
            </button>
          </div>
        </div>
      </div>

      {/* Content viewer */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {viewMode === "markdown" ? (
          <div className="prose max-w-none">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 max-h-96 overflow-y-auto font-mono text-sm text-slate-700 whitespace-pre-wrap break-words">
              {docs.markdown}
            </div>
          </div>
        ) : docs.mermaid_diagram ? (
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-4">Architecture Diagram</h3>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 overflow-x-auto">
              <pre className="text-sm text-slate-700 whitespace-pre-wrap">{docs.mermaid_diagram}</pre>
              <p className="text-xs text-slate-500 mt-4">
                💡 Tip: Copy this diagram and paste it at <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">mermaid.live</a> to view it rendered
              </p>
            </div>
          </div>
        ) : null}
      </div>

      {/* Tech stack */}
      {docs.tech_stack && Object.keys(docs.tech_stack).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-4">🛠️ Technology Stack</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(docs.tech_stack).map(([category, items]) => (
              <div key={category}>
                <h4 className="font-medium text-slate-700 mb-2 capitalize">{category}</h4>
                <div className="flex flex-wrap gap-2">
                  {Array.isArray(items) && items.map((item, idx) => (
                    <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New analysis button */}
      <button
        onClick={onNewAnalysis}
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-4 rounded-lg transition transform hover:scale-105"
      >
        🔄 Analyze Another Repository
      </button>
    </div>
  );
}