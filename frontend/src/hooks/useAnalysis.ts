/**
 * Custom hook for analysis job management.
 */

import { useState, useCallback, useEffect } from "react";
import { Job, StatusResponse, DocsResponse } from "../types";
import { apiClient } from "../api/client";

interface UseAnalysisState {
  job: Job | null;
  status: StatusResponse | null;
  docs: DocsResponse | null;
  loading: boolean;
  error: string | null;
  progress: number;
}

export function useAnalysis() {
  const [state, setState] = useState<UseAnalysisState>({
    job: null,
    status: null,
    docs: null,
    loading: false,
    error: null,
    progress: 0,
  });

  /**
   * Start analysis.
   */
  const startAnalysis = useCallback(
    async (repoPath: string) => {
      setState((s) => ({ ...s, loading: true, error: null, progress: 0 }));

      try {
        const job = await apiClient.analyzeRepository({ repo_path: repoPath });
        setState((s) => ({ ...s, job, progress: 10 }));
        return job;
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : "Unknown error";
        setState((s) => ({ ...s, error: errorMsg, loading: false }));
        throw error;
      }
    },
    []
  );

  /**
   * Poll job status.
   */
  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const status = await apiClient.getJobStatus(jobId);
      setState((s) => ({
        ...s,
        status,
        progress: status.status === "completed" ? 100 : 50,
      }));

      // If completed, fetch docs
      if (status.status === "completed" && status.docs_id) {
        const docs = await apiClient.getDocumentation(status.docs_id);
        setState((s) => ({ ...s, docs, loading: false, progress: 100 }));
      }

      return status;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setState((s) => ({ ...s, error: errorMsg }));
      throw error;
    }
  }, []);

  return {
    ...state,
    startAnalysis,
    pollStatus,
  };
}