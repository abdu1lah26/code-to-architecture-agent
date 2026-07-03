/**
 * Custom hook for polling.
 */

import { useEffect, useRef } from "react";

export function usePolling(
  callback: () => Promise<any>,
  interval: number = 2000,
  enabled: boolean = true
) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const poll = async () => {
      try {
        await callback();
      } catch (error) {
        console.error("Polling error:", error);
      }
      timeoutRef.current = setTimeout(poll, interval);
    };

    poll();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [callback, interval, enabled]);
}