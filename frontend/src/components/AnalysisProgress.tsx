import { Job, StatusResponse } from "../types";

interface AnalysisProgressProps {
  job: Job;
  status: StatusResponse | null;
  progress: number;
  onCancel: () => void;
}

export function AnalysisProgress({
  job,
  status,
  progress,
  onCancel,
}: AnalysisProgressProps) {
  const statusMessages = {
    pending: "⏳ Waiting to start...",
    processing: "🔄 Analyzing your code...",
    completed: "✅ Analysis complete!",
    failed: "❌ Analysis failed",
  };

  const currentStatus = status?.status || job.status;
  const message = statusMessages[currentStatus as keyof typeof statusMessages] || "Processing...";

  const steps = [
    { name: "Parsing", status: progress > 10 ? "done" : progress > 0 ? "active" : "pending" },
    { name: "Dependency Analysis", status: progress > 30 ? "done" : progress > 20 ? "active" : "pending" },
    { name: "Pattern Recognition", status: progress > 50 ? "done" : progress > 40 ? "active" : "pending" },
    { name: "Generation", status: progress > 80 ? "done" : progress > 70 ? "active" : "pending" },
    { name: "Finalization", status: progress === 100 ? "done" : progress > 90 ? "active" : "pending" },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Analysis in Progress</h2>

      {/* Status message */}
      <div className="mb-6 text-center">
        <p className="text-lg font-medium text-slate-700">{message}</p>
        {job.repo_path && (
          <p className="text-sm text-slate-500 mt-2">📁 {job.repo_path}</p>
        )}
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-slate-700">Overall Progress</span>
          <span className="text-sm font-bold text-blue-600">{progress}%</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Step indicators */}
      <div className="space-y-3 mb-8">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                step.status === "done"
                  ? "bg-green-500 text-white"
                  : step.status === "active"
                  ? "bg-blue-500 text-white animate-pulse"
                  : "bg-slate-300 text-slate-600"
              }`}
            >
              {step.status === "done" ? "✓" : step.status === "active" ? "→" : "•"}
            </div>
            <span
              className={`text-sm font-medium ${
                step.status === "done"
                  ? "text-green-600"
                  : step.status === "active"
                  ? "text-blue-600"
                  : "text-slate-500"
              }`}
            >
              {step.name}
            </span>
          </div>
        ))}
      </div>

      {/* Error message */}
      {status?.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-medium">❌ Error occurred</p>
          <p className="text-red-700 text-sm mt-1">{status.error_message}</p>
        </div>
      )}

      {/* Cancel button */}
      <button
        onClick={onCancel}
        className="w-full bg-slate-300 hover:bg-slate-400 text-slate-700 font-medium py-2 px-4 rounded-lg transition"
      >
        Start Over
      </button>
    </div>
  );
}