import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { token, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [token, navigate]);

  useEffect(() => {
    const verifyToken = searchParams.get("token");
    if (!verifyToken) return;

    async function verify() {
      try {
        const response = await fetch(`/api/auth/verify?token=${verifyToken}`);
        const data = await response.json();

        if (!response.ok) {
          setError(data?.detail?.message || "Invalid or expired link.");
          return;
        }

        login(data.token, { id: data.user_id, email: data.email });
        navigate("/dashboard", { replace: true });
      } catch {
        setError("Something went wrong verifying your login link.");
      }
    }

    verify();
  }, [searchParams, login, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/dev-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.detail?.message || "Could not log in.");
        return;
      }

      login(data.token, { id: data.user_id, email: data.email });
      navigate("/dashboard", { replace: true });
    } catch {
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      {/* Decorative background shapes */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-brand-peach rounded-full opacity-60 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-brand-warm rounded-full opacity-60 blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        {/* Logo & tagline */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 bg-brand-red rounded-xl flex items-center justify-center">
              <span className="text-white font-heading font-bold text-lg">N</span>
            </div>
          </div>
          <h1 className="text-4xl font-heading font-bold text-gray-900 tracking-tight">
            Namedropper
          </h1>
          <p className="mt-3 text-gray-500 text-lg">
            Personalize any video with a spoken name.
          </p>
        </div>

        {/* Login card */}
        <div className="card p-8">
          {sent ? (
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-heading font-semibold mb-2">
                Check your email
              </h2>
              <p className="text-gray-500">
                We sent a login link to{" "}
                <span className="font-medium text-gray-900">{email}</span>.
              </p>
              <button
                onClick={() => setSent(false)}
                className="mt-6 text-sm text-brand-red hover:underline font-medium"
              >
                Use a different email
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl
                         focus:ring-2 focus:ring-brand-red/20 focus:border-brand-red
                         outline-none transition-all duration-200
                         bg-gray-50 focus:bg-white"
              />

              {error && (
                <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
                  <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-5 w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Logging in...
                  </span>
                ) : (
                  "Log in"
                )}
              </button>
            </form>
          )}
        </div>

        <p className="mt-8 text-center text-xs text-gray-400">
          Built by SuperStories BV
        </p>
      </div>
    </div>
  );
}
