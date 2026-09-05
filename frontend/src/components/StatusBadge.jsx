const STYLES = {
  NORMAL: "bg-signal-teal/10 text-signal-teal border-signal-teal/30",
  GOOD: "bg-signal-teal/10 text-signal-teal border-signal-teal/30",
  WARNING: "bg-signal-amber/10 text-signal-amber border-signal-amber/30",
  CRITICAL: "bg-signal-red/10 text-signal-red border-signal-red/30",
  NO_DATA: "bg-base-600/20 text-base-400 border-base-600/40",
  UNKNOWN: "bg-base-600/20 text-base-400 border-base-600/40",
  INFO: "bg-signal-blue/10 text-signal-blue border-signal-blue/30",
  CONNECTED: "bg-signal-teal/10 text-signal-teal border-signal-teal/30",
  DISCONNECTED: "bg-signal-red/10 text-signal-red border-signal-red/30",
  DEMO: "bg-signal-blue/10 text-signal-blue border-signal-blue/30",
  ACTIVE: "bg-signal-red/10 text-signal-red border-signal-red/30",
  ACKNOWLEDGED: "bg-signal-amber/10 text-signal-amber border-signal-amber/30",
  RESOLVED: "bg-base-600/20 text-base-400 border-base-600/40",
};

export default function StatusBadge({ status, size = "sm" }) {
  const style = STYLES[status] || STYLES.NO_DATA;
  const sizing = size === "sm" ? "text-[11px] px-2 py-0.5" : "text-xs px-2.5 py-1";
  return (
    <span className={`inline-flex items-center gap-1 rounded border font-medium tracking-wide ${sizing} ${style}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status.replace("_", " ")}
    </span>
  );
}
