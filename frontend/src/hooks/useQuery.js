import { useEffect, useRef, useState, useCallback } from "react";

/**
 * Minimal polling data-fetch hook: calls fetchFn immediately, then again
 * every `intervalMs` (if provided). Deliberately dependency-light - this
 * project doesn't need a full data-fetching library.
 */
export function useQuery(fetchFn, deps = [], intervalMs = 0) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetchRef = useRef(fetchFn);
  fetchRef.current = fetchFn;

  const refetch = useCallback(async () => {
    try {
      const result = await fetchRef.current();
      setData(result);
      setError(null);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const run = async () => {
      try {
        const result = await fetchRef.current();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    run();
    let interval;
    if (intervalMs > 0) {
      interval = setInterval(run, intervalMs);
    }

    return () => {
      cancelled = true;
      if (interval) clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, error, loading, refetch };
}
