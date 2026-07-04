import { useEffect, useState } from "react";
import { Job } from "../types";
import { apiClient } from "../api/client";
import { formatDate } from "../utils/date";

export function JobList() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await apiClient.listJobs(10, 0);
        setJobs(data);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to fetch jobs";
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <div className="animate-spin h-8 w-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        <p className="text-slate-600">Loading jobs...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">❌ {error}</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 text-center">
        <p className="text-slate-600">No analysis jobs yet. Start one above!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200">
        <h3 className="text-lg font-bold text-slate-900">📋 Recent Analysis Jobs</h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase">Repository</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {jobs.map((job) => (
              <tr key={job.job_id} className="hover:bg-slate-50 transition">
                <td className="px-6 py-4 text-sm text-slate-700 truncate">
                  {job.repo_path || job.repo_url || "Unknown"}
                </td>
                <td className="px-6 py-4 text-sm">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      job.status === "completed"
                        ? "bg-green-100 text-green-800"
                        : job.status === "processing"
                        ? "bg-blue-100 text-blue-800"
                        : job.status === "failed"
                        ? "bg-red-100 text-red-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {job.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-600">
                  {formatDate(job.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}