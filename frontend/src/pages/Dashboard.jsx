import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

const STATUS_BADGES = {
  draft: { label: "Draft", className: "bg-gray-100 text-gray-600" },
  processing: { label: "Processing", className: "bg-amber-50 text-amber-700 border border-amber-200" },
  completed: { label: "Completed", className: "bg-emerald-50 text-emerald-700 border border-emerald-200" },
  failed: { label: "Failed", className: "bg-red-50 text-red-700 border border-red-200" },
};

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadProjects() {
      try {
        const response = await fetch("/api/projects");
        const data = await response.json();
        if (!response.ok) throw new Error(data?.detail?.message || "Failed to load projects");
        setProjects(data.projects);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-red rounded-lg flex items-center justify-center">
              <span className="text-white font-heading font-bold text-sm">N</span>
            </div>
            <h1 className="text-xl font-heading font-bold tracking-tight">Namedropper</h1>
          </div>
          <div className="flex items-center gap-5">
            <Link
              to="/manual"
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              Manual
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-heading font-bold tracking-tight">Your projects</h2>
            <p className="text-gray-400 text-sm mt-1">Create personalized videos at scale</p>
          </div>
          <Link to="/projects/new" className="btn-primary flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New project
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-20">
            <svg className="animate-spin w-6 h-6 text-brand-red" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        )}

        {error && (
          <div className="card p-4 border-red-200 bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        )}

        {!loading && projects.length === 0 && (
          <div className="card text-center py-20 px-8">
            <div className="w-16 h-16 bg-brand-peach rounded-2xl flex items-center justify-center mx-auto mb-5">
              <svg className="w-8 h-8 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <h3 className="font-heading font-semibold text-lg text-gray-900 mb-2">
              No projects yet
            </h3>
            <p className="text-gray-400 mb-6 max-w-sm mx-auto">
              Upload a video, add names, and Namedropper creates a personalized version for each person.
            </p>
            <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Create your first project
            </Link>
          </div>
        )}

        {!loading && projects.length > 0 && (
          <div className="grid gap-3">
            {projects.map((project) => {
              const badge = STATUS_BADGES[project.status] || STATUS_BADGES.draft;
              const progress = project.total_names > 0
                ? Math.round((project.completed_names / project.total_names) * 100)
                : 0;

              return (
                <button
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="card-hover p-5 text-left w-full group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <h3 className="font-heading font-semibold text-lg truncate">
                          {project.title || `Project #${project.id}`}
                        </h3>
                        <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${badge.className}`}>
                          {badge.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="text-sm text-gray-400">
                          {project.total_names} names
                        </span>
                        {project.completed_names > 0 && (
                          <>
                            <span className="text-gray-200">|</span>
                            <span className="text-sm text-gray-400">
                              {project.completed_names} completed
                            </span>
                          </>
                        )}
                        <span className="text-gray-200">|</span>
                        <span className="text-sm text-gray-400">
                          {new Date(project.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {project.status === "processing" && project.total_names > 0 && (
                        <div className="mt-3 w-full max-w-xs">
                          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-brand-red rounded-full transition-all duration-500"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                    <svg className="w-5 h-5 text-gray-300 group-hover:text-gray-500 transition-colors ml-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
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
