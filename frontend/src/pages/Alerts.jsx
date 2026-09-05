import { useState } from "react";
import { useQuery } from "../hooks/useQuery";
import { api } from "../services/api";
import AlertItem from "../components/AlertItem";

export default function Alerts() {
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");

  const { data: alerts, refetch } = useQuery(
    () => api.getAlerts({ severity: severity || undefined, status: status || undefined, limit: 100 }),
    [severity, status],
    6000
  );

  async function handleAcknowledge(id) {
    await api.acknowledgeAlert(id);
    refetch();
  }
  async function handleResolve(id) {
    await api.resolveAlert(id);
    refetch();
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-base font-semibold text-base-100">Alerts</h1>
        <div className="flex gap-2">
          <select value={severity} onChange={(e) => setSeverity(e.target.value)}
            className="bg-base-900 border border-base-700 text-sm text-base-200 rounded px-3 py-1.5 focus-ring">
            <option value="">All severities</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)}
            className="bg-base-900 border border-base-700 text-sm text-base-200 rounded px-3 py-1.5 focus-ring">
            <option value="">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {(!alerts || alerts.length === 0) ? (
        <div className="bg-base-900 border border-base-700 rounded-sm p-6 text-center text-sm text-base-500">
          No alerts match the current filters.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map((a) => (
            <AlertItem key={a.id} alert={a} onAcknowledge={handleAcknowledge} onResolve={handleResolve} />
          ))}
        </div>
      )}
    </div>
  );
}
