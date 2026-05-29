-- schema.sql
-- IoT Data Engineering Pipeline PostgreSQL Schema

-- 1. Create raw telemetry data table
CREATE TABLE IF NOT EXISTS telemetry_data (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    temperature NUMERIC(5,2) NOT NULL,
    vibration NUMERIC(4,2) NOT NULL,
    pressure NUMERIC(5,2) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Indexes for optimization
CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON telemetry_data(device_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_inserted_at ON telemetry_data(inserted_at);
