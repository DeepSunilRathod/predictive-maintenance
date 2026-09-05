import { useEffect, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import { AlertTriangle } from "lucide-react";

export default function PredictiveMaintenance() {
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function run() {
      setLoading(true);
      try {
        const latest = await api.getLatestSensors();
        const values = {};
        latest.parameters.forEach((p) => { values[p.parameter] = p.value; });

        if (Object.values(values).some((v) => v === null || v === undefined)) {
          setError("Not enough live sensor data yet to run a prediction.");
          setPrediction(null);
          return;
        }

        const result = await api.runPredict(values);
        setPrediction(result);
        setError(null);
      } catch (e) {
        setError("Could not reach the prediction API.");
      } finally {
        setLoading(false);
      }
    }
    run();
    const interval = setInterval(run, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-5 max-w-3xl">
      <h1 className="text-base font-semibold text-base-100">Predictive Maintenance</h1>

      {loading && <p className="text-sm text-base-500">Running prediction...</p>}
      {error && (
        <div className="bg-base-900 border border-base-700 rounded-sm p-4 flex gap-3 items-start">
          <AlertTriangle className="text-signal-amber shrink-0" size={18} />
          <p className="text-sm text-base-300">{error}</p>
        </div>
      )}

      {prediction && (
        <>
          {!prediction.model_available && (
            <div className="bg-signal-amber/5 border border-signal-amber/30 rounded-sm p-4 text-sm text-signal-amber">
              {prediction.note}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-base-900 border border-base-700 rounded-sm p-5">
              <div className="text-xs text-base-500 mb-1">Failure Probability</div>
              <div className="mono text-3xl text-base-100">
                {prediction.failure_probability !== null ? `${(prediction.failure_probability * 100).toFixed(0)}%` : "—"}
              </div>
            </div>
            <div className="bg-base-900 border border-base-700 rounded-sm p-5">
              <div className="text-xs text-base-500 mb-1">Remaining Useful Life</div>
              <div className="mono text-xl text-base-100">
                {prediction.remaining_useful_life_hours !== null
                  ? `${prediction.remaining_useful_life_hours} hours`
                  : "RUL model not available"}
              </div>
            </div>
          </div>

          <div className="bg-base-900 border border-base-700 rounded-sm p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-base-400">Predicted condition</span>
              <span className="text-sm text-base-100">{prediction.predicted_condition || "—"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-base-400">Confidence</span>
              <span className="text-sm text-base-100 mono">
                {prediction.confidence !== null ? `${(prediction.confidence * 100).toFixed(0)}%` : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-base-400">Status</span>
              <StatusBadge status={prediction.status} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-base-400">Prediction timestamp</span>
              <span className="text-sm text-base-100 mono">
                {new Date(prediction.prediction_timestamp).toLocaleString()}
              </span>
            </div>
          </div>

        </>
      )}
    </div>
  );
}
