import { useState } from "react";
import { Layout } from "./components/Layout";
import { useAnalysis } from "./hooks/useAnalysis";

function App() {
  const [repoPath, setRepoPath] = useState("");
  const { job, status, docs, loading, error, progress, startAnalysis, pollStatus } = useAnalysis();

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoPath.trim()) {
      alert("Please enter a repository path");
      return;
    }

    try {
      const newJob = await startAnalysis(repoPath);
      // Start polling
      const pollJob = async () => {
        if (newJob && !status?.docs_id) {
          await pollStatus(newJob.job_id);
        }
      };
      
      // Poll immediately
      pollJob();
      
      // Then poll every 2 seconds
      const interval = setInterval(pollJob, 2000);
      return () => clearInterval(interval);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <Layout>
      {/* Initial form or results */}
      {!job ? (
        <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Analyze Your Repository</h2>
          
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Repository Path
              </label>
              <input
                type="text"
                placeholder="e.g., D:/projects/my-app or /home/user/projects/my-app"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-slate-500 mt-2">
                Enter the local path to your JavaScript/TypeScript repository
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">❌ Error: {error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              {loading ? "Analyzing..." : "Start Analysis"}
            </button>
          </form>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Analysis progress */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Analysis Progress</h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">Progress</span>
                  <span className="text-sm font-medium text-slate-700">{progress}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>

              <p className="text-slate-600">
                Status: <span className="font-medium capitalize">{status?.status || job?.status}</span>
              </p>

              {status?.error_message && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800">❌ {status.error_message}</p>
                </div>
              )}
            </div>
          </div>

          {/* Documentation viewer */}
          {docs && (
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Generated Documentation</h2>
              
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap text-slate-700 font-mono text-sm overflow-x-auto bg-slate-50 p-4 rounded-lg">
                  {docs.markdown}
                </div>
              </div>

              {docs.mermaid_diagram && (
                <div className="mt-8">
                  <h3 className="text-xl font-bold text-slate-900 mb-4">Architecture Diagram</h3>
                  <pre className="bg-slate-50 p-4 rounded-lg overflow-x-auto">
                    {docs.mermaid_diagram}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}

export default App;