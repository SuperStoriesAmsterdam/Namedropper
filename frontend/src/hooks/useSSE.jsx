import { useEffect, useRef } from "react";
import { useAuth } from "./useAuth";

/**
 * Hook that connects to an SSE endpoint and calls handlers for each event type.
 *
 * @param {string} path - The API path (e.g. "/projects/5/progress")
 * @param {Object} handlers - Map of event name to handler function
 * @param {boolean} enabled - Whether to connect (false to disconnect)
 */
export function useSSE(path, handlers, enabled = true) {
  const { token } = useAuth();
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!enabled || !path || !token) {
      return;
    }

    // EventSource doesn't support custom headers, so pass token as query param
    const url = `/api${path}${path.includes("?") ? "&" : "?"}token=${token}`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    // Register handlers for each event type
    Object.entries(handlers).forEach(([eventName, handler]) => {
      eventSource.addEventListener(eventName, (event) => {
        try {
          const data = JSON.parse(event.data);
          handler(data);
        } catch {
          handler(event.data);
        }
      });
    });

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [path, token, enabled]);
  // Note: handlers intentionally excluded from deps to avoid reconnecting on every render
}
