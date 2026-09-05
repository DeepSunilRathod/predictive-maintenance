import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE, timeout: 8000 });

export const api = {
  getMotorStatus: () => client.get("/api/motor/status").then((r) => r.data),
  getMotorDetails: () => client.get("/api/motor/details").then((r) => r.data),
  updateMotorDetails: (payload) => client.put("/api/motor/details", payload).then((r) => r.data),

  getLatestSensors: () => client.get("/api/sensors/latest").then((r) => r.data),
  getHistory: (range = "1h") => client.get("/api/sensors/history", { params: { range } }).then((r) => r.data),

  getHealth: () => client.get("/api/health").then((r) => r.data),

  getAlerts: (params = {}) => client.get("/api/alerts", { params }).then((r) => r.data),
  acknowledgeAlert: (id) => client.post(`/api/alerts/${id}/acknowledge`).then((r) => r.data),
  resolveAlert: (id) => client.post(`/api/alerts/${id}/resolve`).then((r) => r.data),

  runPredict: (payload) => client.post("/api/predict", payload).then((r) => r.data),

  getDemoMode: () => client.get("/api/settings/demo-mode").then((r) => r.data),
  setDemoMode: (enabled) => client.post("/api/settings/demo-mode", { enabled }).then((r) => r.data),
};
