import { ArrowUp, ArrowDown, Minus, WifiOff } from "lucide-react";
import StatusBadge from "./StatusBadge";

const BORDER_BY_STATUS = {
  NORMAL: "border-l-signal-teal",
  WARNING: "border-l-signal-amber",
  CRITICAL: "border-l-signal-red",
  NO_DATA: "border-l-base-600",
};

const TREND_ICON = { up: ArrowUp, down: ArrowDown, flat: Minus, unknown: Minus };

export default function ParameterCard({ label, param }) {
  const { value, unit, status, trend, min_value, max_value, connected } = param;
  const TrendIcon = TREND_ICON[trend] || Minus;
  const trendColor =
    trend === "up" ? "text-signal-red" : trend === "down" ? "text-signal-blue" : "text-base-400";

  return (
    <div
      className={`bg-base-900 border border-base-700 border-l-4 ${BORDER_BY_STATUS[status] || BORDER_BY_STATUS.NO_DATA} rounded-sm p-4 flex flex-col gap-3`}
    >
      <div className="flex items-start justify-between">
        <span className="text-sm text-base-400 font-medium">{label}</span>
        <StatusBadge status={status} />
      </div>

      <div className="flex items-end gap-2">
        {connected ? (
          <>
            <span className="mono text-3xl font-semibold text-base-100 leading-none">
              {value?.toFixed?.(1) ?? value}
            </span>
            <span className="text-sm text-base-400 mb-0.5">{unit}</span>
            <span className={`ml-auto flex items-center gap-0.5 text-xs mb-1 ${trendColor}`}>
              <TrendIcon size={14} />
            </span>
          </>
        ) : (
          <div className="flex items-center gap-2 text-base-500 py-1">
            <WifiOff size={18} />
            <span className="text-sm">Sensor disconnected / no data</span>
          </div>
        )}
      </div>

      <div className="flex justify-between text-xs text-base-500 mono pt-2 border-t border-base-800">
        <span>Min {min_value !== null && min_value !== undefined ? min_value.toFixed(1) : "--"}</span>
        <span>Max {max_value !== null && max_value !== undefined ? max_value.toFixed(1) : "--"}</span>
      </div>
    </div>
  );
}
