"""
DEFAULT parameter thresholds.

*** IMPORTANT ***
These are PLACEHOLDER values only, structured to be reasonable for a small
230V AC induction motor, so the UI and alerting logic can be exercised before
real thresholds are known. They are NOT derived from your actual motor's
datasheet or from experimental measurements.

Replace these via the `thresholds` database table (see database/schema.sql)
once you have measured your motor's real baseline and safe operating limits.
Values stored in the DB always take priority over this file at runtime -
this file only seeds the table on first startup.
"""

DEFAULT_THRESHOLDS = {
    "temperature": {
        "unit": "°C",
        "normal_max": 60.0,
        "warning_max": 75.0,
        "critical_max": 90.0,
        "source": "placeholder - replace with measured motor datasheet/thermal class limits",
    },
    "current": {
        "unit": "A",
        "normal_max": 3.5,
        "warning_max": 4.5,
        "critical_max": 5.5,
        "source": "placeholder - replace with motor nameplate FLA (full load amps)",
    },
    "vibration": {
        "unit": "mm/s RMS",
        "normal_max": 2.8,
        "warning_max": 4.5,
        "critical_max": 7.1,
        "source": "placeholder - loosely modeled on ISO 10816 Class I zones, verify for your motor",
    },
    "rpm": {
        "unit": "RPM",
        "rated": 1440.0,
        "normal_band_pct": 5.0,
        "warning_band_pct": 10.0,
        "critical_band_pct": 20.0,
        "source": "placeholder - replace with motor nameplate rated RPM and acceptable slip band",
    },
}
