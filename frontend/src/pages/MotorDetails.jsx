import { useEffect, useState } from "react";
import { useQuery } from "../hooks/useQuery";
import { api } from "../services/api";

const FIELDS = [
  { key: "motor_type", label: "Motor Type", type: "text" },
  { key: "rated_voltage", label: "Rated Voltage (V)", type: "number" },
  { key: "rated_power_kw", label: "Rated Power (kW)", type: "number" },
  { key: "rated_rpm", label: "Rated RPM", type: "number" },
  { key: "total_operating_hours", label: "Total Operating Hours", type: "number" },
];

export default function MotorDetails() {
  const { data: motor, refetch } = useQuery(() => api.getMotorDetails(), [], 0);
  const { data: latest } = useQuery(() => api.getLatestSensors(), [], 5000);
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (motor) setForm(motor);
  }, [motor]);

  async function handleSave() {
    setSaving(true);
    try {
      await api.updateMotorDetails(form);
      refetch();
    } finally {
      setSaving(false);
    }
  }

  if (!form) return <p className="text-sm text-base-500">Loading motor details...</p>;

  return (
    <div className="flex flex-col gap-5 max-w-2xl">
      <h1 className="text-base font-semibold text-base-100">Motor Details</h1>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5 flex justify-between items-center">
        <div>
          <div className="text-xs text-base-500">Motor ID</div>
          <div className="text-sm text-base-100 mono">{form.motor_id}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-base-500">Sensor connection</div>
          <div className="text-sm text-base-100">{latest?.demo_mode ? "Demo mode" : "Live"}</div>
        </div>
      </div>

      <div className="bg-base-900 border border-base-700 rounded-sm p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {FIELDS.map(({ key, label, type }) => (
          <label key={key} className="flex flex-col gap-1">
            <span className="text-xs text-base-500">{label}</span>
            <input
              type={type}
              value={form[key] ?? ""}
              onChange={(e) => setForm({ ...form, [key]: type === "number" ? parseFloat(e.target.value) || null : e.target.value })}
              className="bg-base-800 border border-base-700 rounded px-3 py-2 text-sm text-base-100 focus-ring"
            />
          </label>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="self-start text-sm px-4 py-2 rounded bg-signal-teal/10 border border-signal-teal/40 text-signal-teal hover:bg-signal-teal/20 disabled:opacity-50 focus-ring"
      >
        {saving ? "Saving..." : "Save Changes"}
      </button>

      <p className="text-xs text-base-500">
        These fields are configurable and stored in the motor_info database table - they are not hard-coded in the frontend.
      </p>
    </div>
  );
}
