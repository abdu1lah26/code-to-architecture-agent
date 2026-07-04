import { useState } from "react";
import { AnalyzeRequest } from "../types";

interface RepoInputProps {
  onSubmit: (request: AnalyzeRequest) => Promise<void>;
  loading: boolean;
  error?: string;
}

export function RepoInput({ onSubmit, loading, error }: RepoInputProps) {
  const [repoPath, setRepoPath] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [inputType, setInputType] = useState<"path" | "url">("path");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const request: AnalyzeRequest =
      inputType === "path"
        ? { repo_path: repoPath }
        : { repo_url: repoUrl };

    if (!request.repo_path && !request.repo_url) {
      alert("Please enter a repository path or URL");
      return;
    }

    try {
      await onSubmit(request);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Analyze Your Repository</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input type toggle */}
        <div className="flex gap-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="path"
              checked={inputType === "path"}
              onChange={() => setInputType("path")}
              className="mr-2"
            />
            <span className="text-slate-700 font-medium">Local Path</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="url"
              checked={inputType === "url"}
              onChange={() => setInputType("url")}
              className="mr-2"
              disabled
            />
            <span className="text-slate-700 font-medium text-gray-400">GitHub URL (Coming Soon)</span>
          </label>
        </div>

        {/* Path input */}
        {inputType === "path" && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Repository Path
            </label>
            <input
              type="text"
              placeholder="e.g., D:/projects/my-app or /home/user/projects/my-app"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <p className="text-sm text-slate-500 mt-2">
              📁 Absolute path to your JavaScript/TypeScript repository
            </p>
          </div>
        )}

        {/* URL input (disabled for now) */}
        {inputType === "url" && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              GitHub Repository URL
            </label>
            <input
              type="text"
              placeholder="e.g., https://github.com/user/repo"
              disabled
              className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-gray-100 text-gray-500"
            />
            <p className="text-sm text-slate-500 mt-2">
              Coming in v1.1 - Clone & analyze from GitHub directly
            </p>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-medium">❌ Error</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-3 px-4 rounded-lg transition transform hover:scale-105 disabled:scale-100 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
              Analyzing...
            </>
          ) : (
            <>
              🚀 Start Analysis
            </>
          )}
        </button>
      </form>

      {/* Info box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💡 How it works</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Parses your codebase (AST analysis)</li>
          <li>✓ Builds dependency graphs</li>
          <li>✓ Detects architecture patterns</li>
          <li>✓ Generates documentation & diagrams</li>
        </ul>
      </div>
    </div>
  );
}