-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create sensor_readings table (will be converted to hypertable)
CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    sensor_value DOUBLE PRECISION NOT NULL,
    measurement_unit VARCHAR(20),
    data_quality INTEGER CHECK (data_quality >= 0 AND data_quality <= 100),
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);

-- Create indexes for sensor_readings
CREATE INDEX IF NOT EXISTS idx_sensor_readings_well_id ON sensor_readings(well_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_type ON sensor_readings(sensor_type);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_well_timestamp ON sensor_readings(well_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp DESC);

-- Create well_metadata table
CREATE TABLE IF NOT EXISTS well_metadata (
    well_id VARCHAR(50) PRIMARY KEY,
    well_name VARCHAR(100) NOT NULL,
    location_lat DOUBLE PRECISION NOT NULL,
    location_lon DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    equipment_type VARCHAR(50),
    installation_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    last_maintenance DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for well location (for geographic queries)
CREATE INDEX IF NOT EXISTS idx_well_metadata_location ON well_metadata USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_well_metadata_status ON well_metadata(status);

-- Create ML predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    prediction_value DOUBLE PRECISION,
    confidence_score DOUBLE PRECISION CHECK (confidence_score >= 0 AND confidence_score <= 1),
    prediction_type VARCHAR(50),
    features JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert ml_predictions to hypertable
SELECT create_hypertable('ml_predictions', 'timestamp', if_not_exists => TRUE);

-- Create indexes for ml_predictions
CREATE INDEX IF NOT EXISTS idx_ml_predictions_well_id ON ml_predictions(well_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_model_type ON ml_predictions(model_type);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_well_timestamp ON ml_predictions(well_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_timestamp ON ml_predictions(timestamp DESC);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT NOT NULL,
    sensor_type VARCHAR(50),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_well_id ON alerts(well_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- Create data_quality_metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('data_quality_metrics', 'timestamp', if_not_exists => TRUE);

-- Create indexes for data_quality_metrics
CREATE INDEX IF NOT EXISTS idx_data_quality_well_id ON data_quality_metrics(well_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_sensor_type ON data_quality_metrics(sensor_type);

-- Create continuous aggregates for sensor readings (hourly averages)
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    well_id,
    sensor_type,
    AVG(sensor_value) AS avg_value,
    MIN(sensor_value) AS min_value,
    MAX(sensor_value) AS max_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, well_id, sensor_type;

-- Create index on continuous aggregate
CREATE INDEX IF NOT EXISTS idx_sensor_readings_hourly_bucket ON sensor_readings_hourly(bucket DESC, well_id);

-- Create continuous aggregates for sensor readings (daily averages)
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS bucket,
    well_id,
    sensor_type,
    AVG(sensor_value) AS avg_value,
    MIN(sensor_value) AS min_value,
    MAX(sensor_value) AS max_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, well_id, sensor_type;

-- Create index on continuous aggregate
CREATE INDEX IF NOT EXISTS idx_sensor_readings_daily_bucket ON sensor_readings_daily(bucket DESC, well_id);

-- Create retention policy (optional - keeps data for 1 year)
-- SELECT add_retention_policy('sensor_readings', INTERVAL '1 year');

-- Create function to update well_metadata updated_at
CREATE OR REPLACE FUNCTION update_well_metadata_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS trigger_update_well_metadata_updated_at ON well_metadata;
CREATE TRIGGER trigger_update_well_metadata_updated_at
    BEFORE UPDATE ON well_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_well_metadata_updated_at();

-- Create function to calculate location geography from lat/lon
CREATE OR REPLACE FUNCTION update_well_location()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location = ST_SetSRID(ST_MakePoint(NEW.location_lon, NEW.location_lat), 4326)::geography;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for location
DROP TRIGGER IF EXISTS trigger_update_well_location ON well_metadata;
CREATE TRIGGER trigger_update_well_location
    BEFORE INSERT OR UPDATE ON well_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_well_location();
