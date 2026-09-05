const COLOR_BY_STATUS = {
  GOOD: "#2DD9C4",
  WARNING: "#F0A93B",
  CRITICAL: "#EF5A5A",
  UNKNOWN: "#5A6270",
};

export default function HealthGauge({ score, status }) {
  const radius = 80;
  const stroke = 14;
  const normalizedScore = score ?? 0;
  const circumference = Math.PI * radius; // half circle
  const offset = circumference - (normalizedScore / 100) * circumference;
  const color = COLOR_BY_STATUS[status] || COLOR_BY_STATUS.UNKNOWN;

  return (
    <div className="flex flex-col items-center">
      <svg width="220" height="130" viewBox="0 0 220 130">
        <path
          d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none"
          stroke="#2A3038"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        <path
          d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.6s ease, stroke 0.3s ease" }}
        />
        <text x="110" y="95" textAnchor="middle" className="mono" fontSize="36" fontWeight="600" fill="#E7EAEE">
          {score !== null && score !== undefined ? `${score}%` : "--"}
        </text>
      </svg>
      <div className="text-xs text-base-400 -mt-2">Health Score</div>
    </div>
  );
}
