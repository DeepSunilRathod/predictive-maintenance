import StatusBadge from "./StatusBadge";

function formatTime(ts) {
  return new Date(ts).toLocaleString();
}

export default function AlertItem({ alert, onAcknowledge, onResolve }) {
  const borderColor =
    alert.severity === "CRITICAL" ? "border-l-signal-red" :
    alert.severity === "WARNING" ? "border-l-signal-amber" : "border-l-signal-blue";

  return (
    <div className={`bg-base-900 border border-base-700 border-l-4 ${borderColor} rounded-sm p-4`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <StatusBadge status={alert.severity} />
            <span className="text-xs text-base-500 mono">{formatTime(alert.timestamp)}</span>
          </div>
          <p className="text-sm text-base-100 font-medium">{alert.message}</p>
          <p className="text-xs text-base-400 mt-1 mono">
            {alert.parameter} = {alert.value} (threshold {alert.threshold})
          </p>
          {alert.possible_cause && (
            <p className="text-xs text-base-400 mt-2">
              <span className="text-base-500">Possible cause: </span>{alert.possible_cause}
            </p>
          )}
          {alert.recommended_action && (
            <p className="text-xs text-base-400 mt-1">
              <span className="text-base-500">Recommended action: </span>{alert.recommended_action}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <StatusBadge status={alert.status} />
          {alert.status === "ACTIVE" && (
            <div className="flex gap-2">
              <button
                onClick={() => onAcknowledge(alert.id)}
                className="text-xs px-2 py-1 rounded border border-base-600 text-base-300 hover:border-signal-teal hover:text-signal-teal transition-colors focus-ring"
              >
                Acknowledge
              </button>
              <button
                onClick={() => onResolve(alert.id)}
                className="text-xs px-2 py-1 rounded border border-base-600 text-base-300 hover:border-signal-teal hover:text-signal-teal transition-colors focus-ring"
              >
                Resolve
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
