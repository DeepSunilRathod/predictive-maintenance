import { useEffect, useState } from "react";
import { useQuery } from "../../hooks/useQuery";
import { api } from "../../services/api";
import StatusBadge from "../StatusBadge";
import { useDemoMode } from "../../context/DemoModeContext";

export default function Header() {
  const { data: status } = useQuery(() => api.getMotorStatus(), [], 5000);
  const { demoMode } = useDemoMode();
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="h-16 shrink-0 bg-base-900 border-b border-base-800 flex items-center justify-between px-6">
      <div>
        <h1 className="text-sm font-semibold text-base-100">
          IoT-Based Predictive Maintenance System for AC Induction Motor
        </h1>
        <p className="text-xs text-base-500 mono">Motor ID: {status?.motor_id || "MOTOR-001"}</p>
      </div>

      <div className="flex items-center gap-4">
        {demoMode && (
          <span className="text-[11px] font-semibold tracking-wide px-2 py-1 rounded border border-signal-blue/30 bg-signal-blue/10 text-signal-blue">
            DEMO DATA
          </span>
        )}
        <StatusBadge status={status?.connection_status || "DISCONNECTED"} size="md" />
        <div className="text-right">
          <div className="text-xs text-base-400">Last updated</div>
          <div className="text-xs text-base-200 mono">
            {status?.last_updated ? new Date(status.last_updated).toLocaleTimeString() : "--"}
          </div>
        </div>
        <div className="text-right border-l border-base-800 pl-4">
          <div className="text-xs text-base-400">System time</div>
          <div className="text-xs text-base-200 mono">{now.toLocaleTimeString()}</div>
        </div>
      </div>
    </header>
  );
}
