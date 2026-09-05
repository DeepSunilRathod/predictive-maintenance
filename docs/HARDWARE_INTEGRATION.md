# Hardware Integration Guide

This describes how to connect your real microcontroller + sensors so the
dashboard shows live data instead of Demo Mode data.

## 1. How the software already expects hardware

The backend never needed to change for hardware to be added - it was built
API-first:

- `POST /api/sensors/data` accepts a JSON reading from *any* device that can
  make an HTTP request: an ESP32/ESP8266 over Wi-Fi, an Arduino + Ethernet
  shield, or a Raspberry Pi acting as a gateway for sensors on a serial bus.
- The moment a reading arrives with `"source": "real"`, the backend
  **automatically stops the Demo Mode generator** so simulated and real data
  are never mixed.
- Every stored row is tagged `source = 'real'` or `source = 'demo'`, and the
  frontend displays a **DEMO DATA** badge whenever demo rows are being shown,
  so the two can never be confused on screen either.

You do not need to modify any backend or frontend code to go live - only
point your device at the API.

## 2. What you need per parameter

| Parameter   | Typical sensor options                                    | Notes |
|-------------|-------------------------------------------------------------|-------|
| Temperature | Thermocouple + MAX6675/MAX31855, or DS18B20, or PT100 + amp | Mount on motor housing/bearing, not just ambient air |
| Current     | ACS712/ACS758 Hall-effect current sensor, or a CT clamp + burden resistor | Must be rated above the motor's rated current |
| Vibration   | MEMS accelerometer (e.g. ADXL345/MPU6050) or piezo vibration sensor | RMS velocity (mm/s) is the standard industrial unit - convert from raw acceleration if needed |
| RPM         | IR/optical tachometer, Hall-effect sensor + magnet, or rotary encoder | Count pulses over a fixed window to derive RPM |

None of these are prescribed by the software - swap in whatever your lab has
available. The dashboard only cares that it receives a numeric value (or
`null` if a sensor isn't wired up yet) for each parameter.

## 3. Minimal ESP32 (Arduino) example

This posts a reading every 2 seconds. Replace the placeholder read functions
with your actual sensor code.

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* API_URL = "http://<YOUR_BACKEND_IP>:8000/api/sensors/data";
const char* DEVICE_API_KEY = "";  // must match DEVICE_API_KEY in backend/.env, or leave blank

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

float readTemperature() { /* TODO: read from your temperature sensor */ return 0.0; }
float readCurrent()     { /* TODO: read from your current sensor */     return 0.0; }
float readVibration()   { /* TODO: read + process accelerometer */      return 0.0; }
float readRpm()         { /* TODO: derive from pulse counter */         return 0.0; }

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    if (strlen(DEVICE_API_KEY) > 0) {
      http.addHeader("X-Device-Api-Key", DEVICE_API_KEY);
    }

    StaticJsonDocument<256> doc;
    doc["motor_id"] = "MOTOR-001";
    doc["temperature"] = readTemperature();
    doc["current"] = readCurrent();
    doc["vibration"] = readVibration();
    doc["rpm"] = readRpm();
    doc["source"] = "real";

    String payload;
    serializeJson(doc, payload);

    int code = http.POST(payload);
    Serial.printf("POST /api/sensors/data -> %d\n", code);
    http.end();
  }
  delay(2000);
}
```

If a sensor genuinely isn't wired up yet, omit that field (or send `null`)
rather than sending `0` - the dashboard treats missing data as
"disconnected", not as a real zero reading.

## 4. Networking checklist

- The microcontroller and the machine running the FastAPI backend must be on
  the same network (or the backend must be reachable over the internet with
  proper firewall/HTTPS setup for a production deployment).
- Find the backend host's local IP (`ipconfig` on Windows / `ip a` on Linux)
  and use it in `API_URL` above instead of `localhost`.
- If requests fail with a CORS error in the browser console (not from the
  microcontroller - CORS only affects browsers), add your frontend's origin
  to `CORS_ORIGINS` in `backend/.env`.

## 5. Switching off Demo Mode explicitly

Real data arriving automatically stops the generator, but you can also turn
Demo Mode off directly from the dashboard's **Settings** page, or via:

```bash
curl -X POST http://localhost:8000/api/settings/demo-mode \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## 6. Calibrating real thresholds

Once your sensors are live, run the motor under known-safe conditions and
record the readings. Update the `thresholds` table (see
`database/schema.sql`) with your motor's real normal/warning/critical values
- the defaults in `backend/config/thresholds.py` are placeholders only and
say so explicitly in their `source_note` field.
