import { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import { useQuery } from "../../hooks/useQuery";
import { api } from "../../services/api";
import StatusBadge from "../StatusBadge";
import { useDemoMode } from "../../context/DemoModeContext";

export default function Header({ onMenuClick }) {
  const { data: status } = useQuery(() => api.getMotorStatus(), [], 5000);
  const { demoMode } = useDemoMode();
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="h-16 shrink-0 bg-base-900 border-b border-base-800 flex items-center justify-between px-3 md:px-6 gap-2">
      <div className="flex items-center gap-3 min-w-0">
        <button onClick={onMenuClick} className="md:hidden text-base-300 hover:text-base-100 shrink-0">
          <Menu size={22} />
        </button>
        <div className="min-w-0">
          <h1 className="text-sm font-semibold text-base-100 truncate">
            <span className="hidden sm:inline">IoT-Based Predictive Maintenance System for AC Induction Motor</span>
            <span className="sm:hidden">Predictive Maintenance</span>
          </h1>
          <p className="text-xs text-base-500 mono truncate">Motor ID: {status?.motor_id || "MOTOR-001"}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-4 shrink-0">
        {demoMode && (
          <span className="hidden sm:inline text-[11px] font-semibold tracking-wide px-2 py-1 rounded border border-signal-blue/30 bg-signal-blue/10 text-signal-blue">
            DEMO DATA
          </span>
        )}
        <StatusBadge status={status?.connection_status || "DISCONNECTED"} size="md" />
        <div className="hidden lg:block text-right">
          <div className="text-xs text-base-400">Last updated</div>
          <div className="text-xs text-base-200 mono">
            {status?.last_updated ? new Date(status.last_updated).toLocaleTimeString() : "--"}
          </div>
        </div>
        <div className="hidden lg:block text-right border-l border-base-800 pl-4">
          <div className="text-xs text-base-400">System time</div>
          <div className="text-xs text-base-200 mono">{now.toLocaleTimeString()}</div>
        </div>
      </div>
    </header>
  );
}