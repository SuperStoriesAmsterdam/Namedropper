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

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [token, navigate]);

  // Handle magic link verification
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
      const response = await fetch("/api/auth/magic-link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.detail?.message || "Could not send login link.");
        return;
      }

      setSent(true);
    } catch {
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-heading font-bold text-gray-900">
            Namedropper
          </h1>
          <p className="mt-2 text-gray-600">
            Personalize any video with a spoken name.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {sent ? (
            <div className="text-center">
              <div className="text-4xl mb-4">✉️</div>
              <h2 className="text-xl font-heading font-semibold mb-2">
                Check your email
              </h2>
              <p className="text-gray-600">
                We sent a login link to{" "}
                <span className="font-medium text-gray-900">{email}</span>.
                Click the link to log in.
              </p>
              <button
                onClick={() => setSent(false)}
                className="mt-6 text-sm text-brand-red hover:underline"
              >
                Use a different email
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent outline-none"
              />

              {error && (
                <p className="mt-2 text-sm text-red-600">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-4 w-full bg-brand-red text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Sending..." : "Send login link"}
              </button>
            </form>
          )}
        </div>

        <p className="mt-6 text-center text-xs text-gray-400">
          SuperStories BV
        </p>
      </div>
    </div>
  );
}
