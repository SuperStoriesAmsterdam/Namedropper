import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useApi } from "../hooks/useApi";

const STATUS_BADGES = {
  draft: { label: "Draft", className: "bg-gray-100 text-gray-700" },
  processing: { label: "Processing", className: "bg-yellow-100 text-yellow-700" },
  completed: { label: "Completed", className: "bg-green-100 text-green-700" },
  failed: { label: "Failed", className: "bg-red-100 text-red-700" },
};

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { user, logout } = useAuth();
  const { apiFetch } = useApi();
  const navigate = useNavigate();

  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await apiFetch("/projects");
        setProjects(data.projects);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, [apiFetch]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-heading font-bold">Namedropper</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-heading font-semibold">Your projects</h2>
          <Link
            to="/projects/new"
            className="bg-brand-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            New project
          </Link>
        </div>

        {loading && <p className="text-gray-500">Loading projects...</p>}

        {error && <p className="text-red-600">{error}</p>}

        {!loading && projects.length === 0 && (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
            <p className="text-gray-500 mb-4">No projects yet.</p>
            <Link
              to="/projects/new"
              className="text-brand-red hover:underline font-medium"
            >
              Create your first personalized video
            </Link>
          </div>
        )}

        {!loading && projects.length > 0 && (
          <div className="grid gap-4">
            {projects.map((project) => {
              const badge = STATUS_BADGES[project.status] || STATUS_BADGES.draft;

              return (
                <button
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="bg-white rounded-xl border border-gray-200 p-5 text-left hover:border-gray-300 hover:shadow-sm transition-all w-full"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-heading font-semibold text-lg">
                        {project.title || `Project #${project.id}`}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {project.total_names} names
                        {project.completed_names > 0 &&
                          ` · ${project.completed_names} completed`}
                        {" · "}
                        {new Date(project.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span
                      className={`text-xs font-medium px-2.5 py-1 rounded-full ${badge.className}`}
                    >
                      {badge.label}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
