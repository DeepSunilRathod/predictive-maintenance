# IoT-Based Predictive Maintenance System for AC Induction Motor

Final-year engineering project dashboard for monitoring a 230V AC induction
motor's **temperature, current, vibration, and RPM** in real time, with
rule-based alerting and an (optional, honest) ML fault-prediction layer.

```
Frontend  → React + Tailwind + Recharts
Backend   → FastAPI (REST + WebSocket)
Database  → MySQL
ML        → Python + scikit-learn (interface only until you train a real model)
```

## Status of this build

This is **Phase 1: a working core system**, built to run end-to-end today:

- Dashboard, Live Monitoring, Alerts, Historical Data, Motor Details, and
  Settings pages are fully functional against the real API.
- Predictive Maintenance page is fully wired up, but honestly reports
  **"model not available"** until you train a model on real labeled data
  (see `backend/ml/train_model.py`) - it never fabricates accuracy.
- Demo Mode is on by default so you can see the whole system working before
  connecting hardware. See `docs/HARDWARE_INTEGRATION.md` for going live.
- Thresholds are placeholders, clearly labeled as such in
  `backend/config/thresholds.py` - replace them once you've measured your
  actual motor's safe operating limits.

## Project structure

```
predictive-maintenance/
├── backend/
│   ├── main.py                 FastAPI app entrypoint
│   ├── api/routes/              REST endpoints (sensors, alerts, health, predict, motor, settings)
│   ├── api/websocket.py         /ws/live real-time channel
│   ├── config/                  settings.py (.env loader), thresholds.py (placeholder limits)
│   ├── database/                SQLAlchemy models, schema.sql, init_db.py
│   ├── ml/                      preprocessing.py, train_model.py, predict.py (no model.pkl included)
│   ├── schemas/                 Pydantic request/response models
│   ├── services/                threshold evaluation, health scoring, demo generator, websocket manager
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/pages/                Dashboard, LiveMonitoring, HistoricalData, PredictiveMaintenance, Alerts, MotorDetails, Settings
│   ├── src/components/           ParameterCard, HealthGauge, LiveChart, AlertItem, StatusBadge, layout/
│   ├── src/services/             api.js (REST), websocket.js (live channel)
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── API.md
│   ├── HARDWARE_INTEGRATION.md
│   └── DATABASE_SETUP.md
└── README.md   (this file)
```

## 1. Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- MySQL 8.x running locally (see `docs/DATABASE_SETUP.md` for full setup)

## 2. Backend setup

```bash
cd backend
python -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env
# then edit .env with your real MySQL credentials
```

Create the database (see `docs/DATABASE_SETUP.md` for details):

```bash
mysql -u root -p -e "CREATE DATABASE predictive_maintenance CHARACTER SET utf8mb4;"
```

Run the backend (tables + placeholder thresholds are created automatically on startup):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API root: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws/live

Demo Mode starts automatically (`DEMO_MODE_DEFAULT=true` in `.env`), so
synthetic sensor readings begin flowing immediately.

## 3. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **http://localhost:5173** — you should see live-updating parameter
cards, a health gauge, and charts driven by Demo Mode data, clearly labeled
`DEMO DATA` in the header.

## 4. Turning off Demo Mode / going live with real sensors

See `docs/HARDWARE_INTEGRATION.md` for a full guide, including an ESP32
example that POSTs to `/api/sensors/data`. In short: once your device starts
sending readings with `"source": "real"`, the backend automatically stops
the demo generator - no code changes required. You can also toggle Demo Mode
from the dashboard's Settings page.

## 5. Training the ML model (optional)

The prediction endpoint works today and returns an honest
`"MODEL_NOT_AVAILABLE"` response. Once you have a labeled dataset (see
`backend/ml/data/README.md` for the required CSV format):

```bash
cd backend
python -m ml.train_model
```

This reports a real held-out test accuracy and writes `backend/ml/model.pkl`,
which `predict.py` picks up automatically on the next API restart.

## 6. Example API calls

```bash
# Latest sensor readings
curl http://localhost:8000/api/sensors/latest

# Post a real reading from hardware
curl -X POST http://localhost:8000/api/sensors/data \
  -H "Content-Type: application/json" \
  -d '{"motor_id":"MOTOR-001","temperature":45.2,"current":2.8,"vibration":1.4,"rpm":1420,"source":"real"}'

# Run a prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature":45.2,"current":2.8,"vibration":1.4,"rpm":1420}'
```

Full endpoint reference: `docs/API.md`.

## Design notes for your report

- **Separation of concerns**: real sensor data → demo data → rule-based
  alerts → ML prediction are kept as four distinct, clearly labeled paths
  throughout the stack (DB `source` column, API `demo_mode`/`model_available`
  flags, UI badges) - nothing is silently blended.
- **Configurability**: thresholds and motor nameplate data live in the
  database, not hard-coded in the frontend, so they can be updated as you
  gather real measurements without redeploying the UI.
- **Extensibility**: the hardware integration point is a single REST
  endpoint (`POST /api/sensors/data`), so any microcontroller capable of an
  HTTP request can act as the data source without backend changes.
