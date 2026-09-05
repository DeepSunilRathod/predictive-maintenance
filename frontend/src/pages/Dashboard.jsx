import { useEffect, useState } from "react";
import { useQuery } from "../hooks/useQuery";
import { api } from "../services/api";
import ParameterCard from "../components/ParameterCard";
import HealthGauge from "../components/HealthGauge";
import LiveChart from "../components/LiveChart";
import { connectLiveSocket } from "../services/websocket";

const PARAM_LABELS = { temperature: "Temperature", current: "Current", vibration: "Vibration", rpm: "RPM" };

export default function Dashboard() {
  const { data: latest, refetch: refetchLatest } = useQuery(() => api.getLatestSensors(), [], 5000);
  const { data: health, refetch: refetchHealth } = useQuery(() => api.getHealth(), [], 5000);
  const { data: recentAlerts } = useQuery(() => api.getAlerts({ status: "ACTIVE", limit: 5 }), [], 8000);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.getHistory("30m").then(setHistory).catch(() => {});
  }, []);

  useEffect(() => {
    const disconnect = connectLiveSocket((payload) => {
      if (payload.type === "sensor_update") {
        refetchLatest();
        refetchHealth();
        setHistory((prev) => [...prev.slice(-300), { timestamp: payload.timestamp, ...payload.data }]);
      }
    });
    return disconnect;
  }, [refetchLatest, refetchHealth]);

  const params = latest?.parameters || [];
  const getParam = (name) => params.find((p) => p.parameter === name) || {
    unit: "", value: null, status: "NO_DATA", trend: "unknown", min_value: null, max_value: null, connected: false,
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {Object.entries(PARAM_LABELS).map(([key, label]) => (
          <ParameterCard key={key} label={label} param={getParam(key)} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1 bg-base-900 border border-base-700 rounded-sm p-5 flex flex-col items-center justify-center">
          <HealthGauge score={health?.health_score} status={health?.status || "UNKNOWN"} />
          <div className="mt-2 text-center">
            <div className="text-sm font-semibold text-base-100">Motor Health: {health?.status || "UNKNOWN"}</div>
            <div className="text-xs text-base-500 mt-1">Risk level: {health?.risk_level || "UNKNOWN"}</div>
          </div>
          <div className="w-full mt-4 pt-4 border-t border-base-800 text-xs text-base-400 space-y-1">
            <div className="flex justify-between"><span className="text-base-500">Operating time</span><span className="mono">{health?.operating_hours?.toFixed?.(1) ?? 0} h</span></div>
            <div className="flex justify-between"><span className="text-base-500">Last fault</span><span className="text-right">{health?.last_fault_detected || "None recorded"}</span></div>
          </div>
          <p className="mt-3 text-[11px] text-base-500 leading-snug">{health?.recommended_action}</p>
        </div>

        <div className="lg:col-span-2 bg-base-900 border border-base-700 rounded-sm p-5">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-base-100">Temperature — Last 30 Minutes</h2>
          </div>
          <LiveChart data={history} parameter="temperature" />
        </div>
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-base-100">Active Alerts</h2>
          <a href="/alerts" className="text-xs text-signal-teal hover:underline">View all</a>
        </div>
        {(!recentAlerts || recentAlerts.length === 0) ? (
          <p className="text-sm text-base-500">No active alerts. All parameters within configured thresholds.</p>
        ) : (
          <ul className="space-y-2">
            {recentAlerts.map((a) => (
              <li key={a.id} className="flex items-center justify-between text-sm border-b border-base-800 pb-2 last:border-0">
                <span className="text-base-200">{a.message}</span>
                <span className="text-xs text-base-500 mono">{new Date(a.timestamp).toLocaleTimeString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
