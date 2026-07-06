import { useState, useEffect } from "react";
import { Layout } from "./components/Layout";
import { RepoInput } from "./components/RepoInput";
import { AnalysisProgress } from "./components/AnalysisProgress";
import { DocsViewer } from "./components/DocsViewer";
import { JobList } from "./components/JobList";
import { useAnalysis } from "./hooks/useAnalysis";
import { AnalyzeRequest } from "./types";

type AppState = "idle" | "analyzing" | "complete";

function App() {
  const [appState, setAppState] = useState<AppState>("idle");
  const {
    job,
    status,
    docs,
    loading,
    error,
    progress,
    startAnalysis,
    pollStatus,
  } = useAnalysis();

  // Poll job status
  useEffect(() => {
    if (!job || appState !== "analyzing") return;

    const pollInterval = setInterval(async () => {
      try {
        const updatedStatus = await pollStatus(job.job_id);

        if (updatedStatus.status === "completed") {
          setAppState("complete");
          clearInterval(pollInterval);
        } else if (updatedStatus.status === "failed") {
          setAppState("idle");
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [job, appState, pollStatus]);

  const handleAnalyze = async (request: AnalyzeRequest) => {
    try {
      setAppState("analyzing");
      await startAnalysis(request.repo_path || request.repo_url || "");
    } catch (err) {
      console.error(err);
      setAppState("idle");
    }
  };

  const handleNewAnalysis = () => {
    setAppState("idle");
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Main content based on state */}
        {appState === "idle" && (
          <>
            <RepoInput onSubmit={handleAnalyze} loading={loading} error={error} />
            <div className="hidden md:block">
              <JobList />
            </div>
          </>
        )}

        {appState === "analyzing" && job && (
          <AnalysisProgress
            job={job}
            status={status}
            progress={progress}
            onCancel={handleNewAnalysis}
          />
        )}

        {appState === "complete" && docs && job && (
          <DocsViewer
            docs={docs}
            jobId={job.job_id}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </div>
    </Layout>
  );
}

export default App;