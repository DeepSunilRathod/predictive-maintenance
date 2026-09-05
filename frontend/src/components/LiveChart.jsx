import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = { temperature: "#EF5A5A", current: "#F0A93B", vibration: "#4C8DFF", rpm: "#2DD9C4" };
const LABELS = { temperature: "Temperature (°C)", current: "Current (A)", vibration: "Vibration (mm/s RMS)", rpm: "RPM" };

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function LiveChart({ data, parameter }) {
  const chartData = data.map((row) => ({
    time: formatTime(row.timestamp),
    value: row[parameter],
  }));

  return (
    <div className="h-72 w-full">
      {chartData.length === 0 ? (
        <div className="h-full flex items-center justify-center text-base-500 text-sm">
          No data in this time range yet.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A3038" />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#838B99" }} minTickGap={30} />
            <YAxis tick={{ fontSize: 11, fill: "#838B99" }} domain={["auto", "auto"]} />
            <Tooltip
              contentStyle={{ background: "#181C22", border: "1px solid #2A3038", borderRadius: 4, fontSize: 12 }}
              labelStyle={{ color: "#AAB2BE" }}
            />
            <Line
              type="monotone"
              dataKey="value"
              name={LABELS[parameter]}
              stroke={COLORS[parameter]}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
