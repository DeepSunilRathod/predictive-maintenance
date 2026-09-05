import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import LiveChart from "../components/LiveChart";

const PARAMS = [
  { key: "temperature", label: "Temperature (°C)" },
  { key: "current", label: "Current (A)" },
  { key: "vibration", label: "Vibration (mm/s RMS)" },
  { key: "rpm", label: "RPM" },
];

function toCsv(rows) {
  const header = "timestamp,temperature,current,vibration,rpm,source\n";
  const body = rows
    .map((r) => [r.timestamp, r.temperature, r.current, r.vibration, r.rpm, r.source].join(","))
    .join("\n");
  return header + body;
}

export default function HistoricalData() {
  const [parameter, setParameter] = useState("temperature");
  const [range, setRange] = useState("24h");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getHistory(range).then(setRows).catch(() => {}).finally(() => setLoading(false));
  }, [range]);

  const stats = useMemo(() => {
    const values = rows.map((r) => r[parameter]).filter((v) => v !== null && v !== undefined);
    if (values.length === 0) return { min: null, max: null, avg: null, count: 0 };
    const sum = values.reduce((a, b) => a + b, 0);
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: sum / values.length,
      count: values.length,
    };
  }, [rows, parameter]);

  const [alertCount, setAlertCount] = useState(null);
  useEffect(() => {
    api.getAlerts({ limit: 500 }).then((alerts) => {
      const cutoffMinutes = { "1m": 1, "5m": 5, "30m": 30, "1h": 60, "24h": 1440 }[range] || 1440;
      const cutoff = Date.now() - cutoffMinutes * 60 * 1000;
      const inRange = alerts.filter((a) => new Date(a.timestamp).getTime() >= cutoff && a.parameter === parameter);
      setAlertCount(inRange.length);
    }).catch(() => setAlertCount(null));
  }, [range, parameter]);

  function handleExport() {
    const csv = toCsv(rows);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sensor_history_${parameter}_${range}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-base font-semibold text-base-100">Historical Data</h1>
        <button
          onClick={handleExport}
          disabled={rows.length === 0}
          className="text-xs px-3 py-1.5 rounded border border-base-700 text-base-300 hover:border-signal-teal hover:text-signal-teal disabled:opacity-40 focus-ring"
        >
          Export CSV
        </button>
      </div>

      <div className="flex flex-wrap gap-4">
        <select
          value={parameter}
          onChange={(e) => setParameter(e.target.value)}
          className="bg-base-900 border border-base-700 text-sm text-base-200 rounded px-3 py-1.5 focus-ring"
        >
          {PARAMS.map((p) => <option key={p.key} value={p.key}>{p.label}</option>)}
        </select>
        <select
          value={range}
          onChange={(e) => setRange(e.target.value)}
          className="bg-base-900 border border-base-700 text-sm text-base-200 rounded px-3 py-1.5 focus-ring"
        >
          <option value="1m">Last 1 minute</option>
          <option value="5m">Last 5 minutes</option>
          <option value="30m">Last 30 minutes</option>
          <option value="1h">Last 1 hour</option>
          <option value="24h">Last 24 hours</option>
        </select>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ["Minimum", stats.min],
          ["Maximum", stats.max],
          ["Average", stats.avg],
          ["Alerts", alertCount],
        ].map(([label, value]) => (
          <div key={label} className="bg-base-900 border border-base-700 rounded-sm p-4">
            <div className="text-xs text-base-500">{label}</div>
            <div className="mono text-xl text-base-100 mt-1">
              {value === null || value === undefined ? "--" : typeof value === "number" ? value.toFixed(label === "Alerts" ? 0 : 2) : value}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5">
        {loading ? (
          <div className="h-72 flex items-center justify-center text-base-500 text-sm">Loading...</div>
        ) : (
          <LiveChart data={rows} parameter={parameter} />
        )}
      </div>
    </div>
  );
}
