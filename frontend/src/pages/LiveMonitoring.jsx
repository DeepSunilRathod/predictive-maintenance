import { useEffect, useState } from "react";
import { api } from "../services/api";
import LiveChart from "../components/LiveChart";
import { connectLiveSocket } from "../services/websocket";

const PARAMS = [
  { key: "temperature", label: "Temperature (°C)" },
  { key: "current", label: "Current (A)" },
  { key: "vibration", label: "Vibration (mm/s RMS)" },
  { key: "rpm", label: "RPM" },
];

const RANGES = [
  { key: "1m", label: "Last 1 min" },
  { key: "5m", label: "Last 5 min" },
  { key: "30m", label: "Last 30 min" },
  { key: "1h", label: "Last 1 hour" },
  { key: "24h", label: "Last 24 hours" },
];

export default function LiveMonitoring() {
  const [parameter, setParameter] = useState("temperature");
  const [range, setRange] = useState("30m");
  const [history, setHistory] = useState([]);
  const [wsStatus, setWsStatus] = useState("connecting");

  useEffect(() => {
    let cancelled = false;
    api.getHistory(range).then((rows) => { if (!cancelled) setHistory(rows); }).catch(() => {});
    return () => { cancelled = true; };
  }, [range]);

  useEffect(() => {
    const disconnect = connectLiveSocket(
      (payload) => {
        if (payload.type === "sensor_update") {
          setHistory((prev) => [...prev.slice(-500), { timestamp: payload.timestamp, ...payload.data }]);
        }
      },
      setWsStatus
    );
    return disconnect;
  }, []);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-base font-semibold text-base-100">Live Monitoring</h1>
          <p className="text-xs text-base-500 mt-0.5">
            Live channel: <span className={wsStatus === "connected" ? "text-signal-teal" : "text-signal-red"}>{wsStatus}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {PARAMS.map((p) => (
            <button
              key={p.key}
              onClick={() => setParameter(p.key)}
              className={`text-xs px-3 py-1.5 rounded border transition-colors focus-ring ${
                parameter === p.key
                  ? "border-signal-teal text-signal-teal bg-signal-teal/10"
                  : "border-base-700 text-base-400 hover:text-base-100"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {RANGES.map((r) => (
          <button
            key={r.key}
            onClick={() => setRange(r.key)}
            className={`text-xs px-3 py-1 rounded border transition-colors focus-ring ${
              range === r.key
                ? "border-signal-blue text-signal-blue bg-signal-blue/10"
                : "border-base-700 text-base-500 hover:text-base-200"
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5">
        <LiveChart data={history} parameter={parameter} />
      </div>
    </div>
  );
}
