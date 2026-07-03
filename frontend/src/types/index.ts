/**
 * Type definitions for the application.
 */

export interface Job {
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  repo_url?: string;
  repo_path?: string;
  created_at?: string;
  error_message?: string;
}

export interface StatusResponse {
  job_id: string;
  status: string;
  progress?: number;
  error_message?: string | null;
  docs_id?: string;
}

export interface DocsResponse {
  docs_id: string;
  job_id: string;
  markdown: string;
  mermaid_diagram?: string;
  tech_stack?: Record<string, string[]>;
  modules?: Record<string, number>;
}

export interface AnalyzeRequest {
  repo_url?: string;
  repo_path?: string;
}