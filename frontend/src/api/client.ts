/**
 * API client for backend communication.
 */

import { AnalyzeRequest, Job, StatusResponse, DocsResponse, AnswerResponse, QAHistoryItem } from "../types";

const API_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Start code analysis.
   */
  async analyzeRepository(request: AnalyzeRequest): Promise<Job> {
    const response = await fetch(`${this.baseUrl}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }

    return response.json();
  }

  /**
   * Get job status.
   */
  async getJobStatus(jobId: string): Promise<StatusResponse> {
    const response = await fetch(`${this.baseUrl}/api/status/${jobId}`);

    if (!response.ok) {
      throw new Error("Failed to fetch job status");
    }

    return response.json();
  }

  /**
   * Get generated documentation.
   */
  async getDocumentation(docsId: string): Promise<DocsResponse> {
    const response = await fetch(`${this.baseUrl}/api/docs/${docsId}`);

    if (!response.ok) {
      throw new Error("Failed to fetch documentation");
    }

    return response.json();
  }

  /**
   * List all jobs.
   */
  async listJobs(limit: number = 20, offset: number = 0): Promise<Job[]> {
    const response = await fetch(
      `${this.baseUrl}/api/jobs?limit=${limit}&offset=${offset}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch jobs");
    }

    return response.json();
  }

  /**
   * Health check.
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  // Add these methods to the ApiClient class

  /**
   * Ask a question about the code.
   */
  async askQuestion(
    jobId: string,
    question: string,
    topK: number = 5,
  ): Promise<AnswerResponse> {
    const response = await fetch(`${this.baseUrl}/api/ask/${jobId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK }),
    });

    if (!response.ok) {
      throw new Error("Failed to get answer");
    }

    return response.json();
  }

  /**
   * Get Q&A history for a job.
   */
  async getQAHistory(jobId: string): Promise<QAHistoryItem[]> {
    const response = await fetch(`${this.baseUrl}/api/qa-history/${jobId}`);

    if (!response.ok) {
      throw new Error("Failed to fetch Q&A history");
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
