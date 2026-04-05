import { useCallback } from "react";

/**
 * Hook that returns a fetch wrapper for API calls.
 * No auth needed — internal tool.
 */
export function useApi() {
  const apiFetch = useCallback(
    async (path, options = {}) => {
      const headers = {
        ...(options.headers || {}),
      };

      // Don't set Content-Type for FormData (file uploads)
      if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
      }

      const response = await fetch(`/api${path}`, {
        ...options,
        headers,
      });

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
    []
  );

  return { apiFetch };
}
