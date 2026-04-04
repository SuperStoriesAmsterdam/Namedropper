import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { useSSE } from "../hooks/useSSE";

const VIDEO_STATUS = {
  pending: { label: "Pending", className: "bg-gray-100 text-gray-600" },
  generating_audio: {
    label: "Generating audio",
    className: "bg-yellow-100 text-yellow-700",
  },
  splicing: { label: "Splicing", className: "bg-yellow-100 text-yellow-700" },
  uploading: { label: "Uploading", className: "bg-blue-100 text-blue-700" },
  completed: { label: "Completed", className: "bg-green-100 text-green-700" },
  failed: { label: "Failed", className: "bg-red-100 text-red-700" },
};

export default function ProjectDetail() {
  const { id } = useParams();
  const { apiFetch } = useApi();

  const [project, setProject] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadStatus, setDownloadStatus] = useState(null);

  const isProcessing = project?.status === "processing";

  // Load project and videos
  const loadData = useCallback(async () => {
    try {
      const [projectData, videosData] = await Promise.all([
        apiFetch(`/projects/${id}`),
        apiFetch(`/projects/${id}/videos?per_page=500`),
      ]);
      setProject(projectData);
      setVideos(videosData.videos);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id, apiFetch]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // SSE for real-time progress
  useSSE(
    `/projects/${id}/progress`,
    {
      video_completed: (data) => {
        setVideos((prev) =>
          prev.map((v) =>
            v.id === data.video_id ? { ...v, status: "completed" } : v
          )
        );
        setProject((prev) =>
          prev
            ? { ...prev, completed_names: data.completed, total_names: data.total }
            : prev
        );
      },
      video_failed: (data) => {
        setVideos((prev) =>
          prev.map((v) =>
            v.id === data.video_id
              ? { ...v, status: "failed", error_message: data.error }
              : v
          )
        );
      },
      project_completed: () => {
        setProject((prev) => (prev ? { ...prev, status: "completed" } : prev));
        // Reload to get final URLs
        loadData();
      },
    },
    isProcessing
  );

  async function handleDownloadAll() {
    setDownloadStatus("preparing");
    try {
      const data = await apiFetch(`/projects/${id}/download`);
      if (data.status === "ready") {
        window.open(data.download_url, "_blank");
        setDownloadStatus(null);
      } else {
        setDownloadStatus("preparing");
        // Poll until ready
        const interval = setInterval(async () => {
          try {
            const check = await apiFetch(`/projects/${id}/download`);
            if (check.status === "ready") {
              clearInterval(interval);
              window.open(check.download_url, "_blank");
              setDownloadStatus(null);
            }
          } catch {
            clearInterval(interval);
            setDownloadStatus(null);
          }
        }, 3000);
      }
    } catch (err) {
      setError(err.message);
      setDownloadStatus(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading project...</p>
      </div>
    );
  }

  if (error && !project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  const completedCount = videos.filter((v) => v.status === "completed").length;
  const failedCount = videos.filter((v) => v.status === "failed").length;
  const progressPercent =
    project.total_names > 0
      ? Math.round((completedCount / project.total_names) * 100)
      : 0;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="text-xl font-heading font-bold">
            Namedropper
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Project header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-heading font-semibold">
              {project.title || `Project #${project.id}`}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Created {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>

          {completedCount > 0 && (
            <button
              onClick={handleDownloadAll}
              disabled={downloadStatus === "preparing"}
              className="bg-brand-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
            >
              {downloadStatus === "preparing"
                ? "Preparing ZIP..."
                : `Download all (${completedCount})`}
            </button>
          )}
        </div>

        {/* Progress bar */}
        {(isProcessing || project.status === "completed") && (
          <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {isProcessing ? "Processing..." : "Complete"}
              </span>
              <span className="text-sm text-gray-500">
                {completedCount} of {project.total_names}
                {failedCount > 0 && ` (${failedCount} failed)`}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  project.status === "completed"
                    ? "bg-green-500"
                    : "bg-brand-red"
                }`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}

        {/* Video grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video) => {
            const status = VIDEO_STATUS[video.status] || VIDEO_STATUS.pending;

            return (
              <div
                key={video.id}
                className="bg-white rounded-xl border border-gray-200 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-lg">{video.first_name}</h3>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${status.className}`}
                  >
                    {status.label}
                  </span>
                </div>

                {video.status === "completed" && video.output_video_url && (
                  <div>
                    <video
                      src={video.output_video_url}
                      controls
                      preload="none"
                      className="w-full rounded-lg bg-black mb-2"
                      style={{ maxHeight: "200px" }}
                    />
                    <a
                      href={video.output_video_url}
                      download={`${video.first_name}.mp4`}
                      className="text-sm text-brand-red hover:underline"
                    >
                      Download
                    </a>
                  </div>
                )}

                {video.status === "failed" && video.error_message && (
                  <p className="text-sm text-red-600">{video.error_message}</p>
                )}

                {["pending", "generating_audio", "splicing", "uploading"].includes(
                  video.status
                ) && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <div className="w-4 h-4 border-2 border-gray-300 border-t-brand-red rounded-full animate-spin" />
                    {status.label}...
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      </main>
    </div>
  );
}
