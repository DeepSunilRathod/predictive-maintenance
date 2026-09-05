-- ============================================================================
-- Predictive Maintenance System - MySQL Schema
-- Run this after creating the database, e.g.:
--   mysql -u root -p < backend/database/schema.sql
-- (or let init_db.py create the tables from the SQLAlchemy models instead)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS predictive_maintenance
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE predictive_maintenance;

-- Raw sensor readings (real hardware OR demo generator, distinguished by `source`)
CREATE TABLE IF NOT EXISTS sensor_data (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    motor_id    VARCHAR(64) NOT NULL,
    timestamp   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    temperature FLOAT NULL,
    current     FLOAT NULL,
    vibration   FLOAT NULL,
    rpm         FLOAT NULL,
    source      VARCHAR(16) NOT NULL DEFAULT 'real',   -- 'real' | 'demo'
    INDEX idx_motor_time (motor_id, timestamp)
) ENGINE=InnoDB;

-- Threshold-crossing alerts
CREATE TABLE IF NOT EXISTS alerts (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    motor_id            VARCHAR(64) NOT NULL,
    timestamp           DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    parameter           VARCHAR(32) NOT NULL,
    value               FLOAT NOT NULL,
    threshold           FLOAT NOT NULL,
    severity            VARCHAR(16) NOT NULL,          -- INFO | WARNING | CRITICAL
    message             VARCHAR(255) NOT NULL,
    possible_cause      VARCHAR(255) NULL,
    recommended_action  VARCHAR(255) NULL,
    status              VARCHAR(16) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE | ACKNOWLEDGED | RESOLVED
    INDEX idx_motor_time_alert (motor_id, timestamp),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Configurable thresholds (overrides config/thresholds.py defaults at runtime)
CREATE TABLE IF NOT EXISTS thresholds (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    parameter     VARCHAR(32) NOT NULL UNIQUE,
    unit          VARCHAR(32) NOT NULL DEFAULT '',
    normal_max    FLOAT NULL,
    warning_max   FLOAT NULL,
    critical_max  FLOAT NULL,
    extra_json    TEXT NULL,
    source_note   VARCHAR(255) NULL,
    updated_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB;

-- Motor nameplate / metadata
CREATE TABLE IF NOT EXISTS motor_info (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    motor_id               VARCHAR(64) NOT NULL UNIQUE,
    motor_type             VARCHAR(64) NULL,
    rated_voltage          FLOAT NULL,
    rated_power_kw         FLOAT NULL,
    rated_rpm              FLOAT NULL,
    installation_date      DATETIME NULL,
    total_operating_hours  FLOAT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- Small key/value table for runtime toggles (e.g. demo_mode = 'true')
CREATE TABLE IF NOT EXISTS system_settings (
    `key`    VARCHAR(64) PRIMARY KEY,
    `value`  VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- Seed default motor row and demo-mode setting (safe to re-run)
INSERT IGNORE INTO motor_info (motor_id, motor_type, rated_voltage, rated_power_kw, rated_rpm)
VALUES ('MOTOR-001', '3-phase AC induction motor', 230, NULL, NULL);

INSERT IGNORE INTO system_settings (`key`, `value`) VALUES ('demo_mode', 'true');
