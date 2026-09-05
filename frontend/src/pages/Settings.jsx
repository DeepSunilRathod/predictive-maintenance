import { useEffect, useState } from "react";
import { useDemoMode } from "../context/DemoModeContext";
import { API_BASE } from "../services/api";

export default function Settings() {
  const { demoMode, setDemoMode, loaded } = useDemoMode();
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
  }, [theme]);

  return (
    <div className="flex flex-col gap-5 max-w-2xl">
      <h1 className="text-base font-semibold text-base-100">Settings</h1>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5 flex items-center justify-between">
        <div>
          <div className="text-sm text-base-100 font-medium">Demo Mode</div>
          <p className="text-xs text-base-500 mt-1 max-w-md">
            When ON, the dashboard shows clearly-labeled simulated sensor data so it can be tested
            without hardware. When OFF, it only shows data received from real sensors via the API/WebSocket.
          </p>
        </div>
        <button
          disabled={!loaded}
          onClick={() => setDemoMode(!demoMode)}
          className={`w-12 h-6 rounded-full relative transition-colors focus-ring ${demoMode ? "bg-signal-teal" : "bg-base-700"}`}
        >
          <span
            className={`absolute top-0.5 w-5 h-5 rounded-full bg-base-950 transition-transform ${demoMode ? "translate-x-6" : "translate-x-0.5"}`}
          />
        </button>
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5 flex items-center justify-between">
        <div>
          <div className="text-sm text-base-100 font-medium">Appearance</div>
          <p className="text-xs text-base-500 mt-1">Dashboard color theme.</p>
        </div>
        <div className="flex gap-2">
          {["dark", "light"].map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`text-xs px-3 py-1.5 rounded border capitalize focus-ring ${
                theme === t ? "border-signal-teal text-signal-teal bg-signal-teal/10" : "border-base-700 text-base-400"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5">
        <div className="text-sm text-base-100 font-medium mb-2">Connection</div>
        <div className="text-xs text-base-400 mono">API base URL: {API_BASE}</div>
        <p className="text-xs text-base-500 mt-2">
          Threshold values are configured on the backend (database table <code className="mono">thresholds</code>),
          not in this UI, so they stay consistent across every client. Edit them via the database or a future
          admin endpoint once your motor's real limits are known.
        </p>
      </div>
    </div>
  );
}
