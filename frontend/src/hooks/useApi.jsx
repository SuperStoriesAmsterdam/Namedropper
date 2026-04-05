import { useAuth } from "./useAuth";
import { useCallback } from "react";

/**
 * Hook that returns a fetch wrapper with authentication headers.
 * Automatically adds the Bearer token and handles JSON parsing.
 */
export function useApi() {
  const { token, logout } = useAuth();

  const apiFetch = useCallback(
    async (path, options = {}) => {
      const headers = {
        ...(options.headers || {}),
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // Don't set Content-Type for FormData (file uploads)
      if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
      }

      const response = await fetch(`/api${path}`, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        logout();
        throw new Error("Session expired. Please log in again.");
      }

      if (response.status === 204) {
        return null;
      }

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = data?.message || data?.detail?.message || "Something went wrong.";
        throw new Error(errorMessage);
      }

      return data;
    },
    [token, logout]
  );

  return { apiFetch };
}
