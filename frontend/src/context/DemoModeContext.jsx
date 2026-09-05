import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "../services/api";

const DemoModeContext = createContext(null);

export function DemoModeProvider({ children }) {
  const [demoMode, setDemoModeState] = useState(true);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api.getDemoMode()
      .then((r) => setDemoModeState(r.enabled))
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  const setDemoMode = useCallback(async (enabled) => {
    setDemoModeState(enabled); // optimistic
    try {
      await api.setDemoMode(enabled);
    } catch (e) {
      console.error("Failed to update demo mode", e);
    }
  }, []);

  return (
    <DemoModeContext.Provider value={{ demoMode, setDemoMode, loaded }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export function useDemoMode() {
  const ctx = useContext(DemoModeContext);
  if (!ctx) throw new Error("useDemoMode must be used within DemoModeProvider");
  return ctx;
}
