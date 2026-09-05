import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";
import Dashboard from "./pages/Dashboard";
import LiveMonitoring from "./pages/LiveMonitoring";
import HistoricalData from "./pages/HistoricalData";
import PredictiveMaintenance from "./pages/PredictiveMaintenance";
import Alerts from "./pages/Alerts";
import MotorDetails from "./pages/MotorDetails";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <div className="flex h-screen bg-base-950">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live" element={<LiveMonitoring />} />
            <Route path="/history" element={<HistoricalData />} />
            <Route path="/predictive" element={<PredictiveMaintenance />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/motor" element={<MotorDetails />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
