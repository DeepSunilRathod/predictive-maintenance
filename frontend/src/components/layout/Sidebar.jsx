import { NavLink } from "react-router-dom";
import { LayoutDashboard, Activity, History, Brain, Bell, Settings2, Info, Gauge, X } from "lucide-react";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/live", label: "Live Monitoring", icon: Activity },
  { to: "/history", label: "Historical Data", icon: History },
  { to: "/predictive", label: "Predictive Maintenance", icon: Brain },
  { to: "/alerts", label: "Alerts", icon: Bell },
  { to: "/motor", label: "Motor Details", icon: Info },
  { to: "/settings", label: "Settings", icon: Settings2 },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <aside
      className={`
        fixed md:static inset-y-0 left-0 z-40
        w-60 shrink-0 bg-base-900 border-r border-base-800 flex flex-col
        transform transition-transform duration-200 ease-in-out
        ${isOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0
      `}
    >
      <div className="h-16 flex items-center justify-between gap-2 px-5 border-b border-base-800">
        <div className="flex items-center gap-2">
          <Gauge className="text-signal-teal" size={22} />
          <div className="leading-tight">
            <div className="text-sm font-semibold text-base-100">PredictMaint</div>
            <div className="text-[11px] text-base-500">Motor Health System</div>
          </div>
        </div>
        <button onClick={onClose} className="md:hidden text-base-400 hover:text-base-100">
          <X size={20} />
        </button>
      </div>
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm border-l-2 transition-colors ${
                isActive
                  ? "border-l-signal-teal text-signal-teal bg-signal-teal/5"
                  : "border-l-transparent text-base-400 hover:text-base-100 hover:bg-base-800"
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-base-800 text-[11px] text-base-500">
        IoT Predictive Maintenance
        <br />
        230V AC Induction Motor
      </div>
    </aside>
  );
}