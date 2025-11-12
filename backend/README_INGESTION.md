# راهنمای Data Ingestion

سیستم Data Ingestion برای دریافت داده‌های real-time از منابع مختلف طراحی شده است.

## منابع داده پشتیبانی شده

### 1. MQTT (IoT Sensors)
برای دریافت داده از سنسورهای IoT که از پروتکل MQTT استفاده می‌کنند.

### 2. OPC-UA (Industrial Systems)
برای اتصال به سیستم‌های صنعتی که از پروتکل OPC-UA استفاده می‌کنند.

### 3. REST API
برای دریافت داده از طریق HTTP REST API.

## معماری

```
[Data Sources] → [Ingestion Service] → [Kafka] → [Processing Pipeline]
     ↓                ↓                    ↓              ↓
  MQTT          Validation          Message Queue    Database
  OPC-UA         Normalization       Streaming        Analytics
  REST API       Quality Check
```

## استفاده

### 1. REST API Ingestion

#### Ingest Single Sensor Reading
```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/sensor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "well_id": "Well_01",
    "sensor_type": "motor_temperature",
    "sensor_value": 75.5,
    "measurement_unit": "C",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

#### Ingest Batch Data
```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/sensor/batch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "well_id": "Well_01",
        "sensor_type": "motor_temperature",
        "sensor_value": 75.5
      },
      {
        "well_id": "Well_01",
        "sensor_type": "intake_pressure",
        "sensor_value": 500.0
      }
    ]
  }'
```

#### Ingest Raw Data
```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/raw" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor_001",
    "metric": "temperature",
    "value": 75.5,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

### 2. MQTT Ingestion

#### راه‌اندازی MQTT Broker (Mosquitto)
```bash
# Install Mosquitto
sudo apt-get install mosquitto mosquitto-clients

# Start Mosquitto
mosquitto -c /etc/mosquitto/mosquitto.conf
```

#### راه‌اندازی MQTT Ingestion
```bash
cd backend
python scripts/start_mqtt_ingestion.py
```

#### پیکربندی MQTT Topics
MQTT client به صورت پیش‌فرض به این topics گوش می‌دهد:
- `sensors/+/+` - sensors/well_id/sensor_type
- `wells/+/data` - wells/well_id/data

#### ارسال داده تست به MQTT
```bash
mosquitto_pub -h localhost -t "sensors/Well_01/motor_temperature" \
  -m '{"well_id": "Well_01", "sensor_type": "motor_temperature", "sensor_value": 75.5}'
```

### 3. OPC-UA Ingestion

#### راه‌اندازی OPC-UA Server (FreeOpcUa)
```bash
# Install FreeOpcUa server
pip install freeopcua

# Run server
python -m opcua.server
```

#### راه‌اندازی OPC-UA Ingestion
```bash
cd backend
python scripts/start_opcua_ingestion.py
```

#### پیکربندی Node IDs
در فایل `start_opcua_ingestion.py` می‌توانید Node IDs را تنظیم کنید:
```python
node_ids = [
    "ns=2;s=Well_01.MotorTemperature",
    "ns=2;s=Well_01.IntakePressure",
]
```

## Data Validation

سیستم به صورت خودکار داده‌های دریافتی را validate می‌کند:

### Validation Rules
- **Required Fields**: well_id, sensor_type, sensor_value
- **Value Ranges**: بررسی محدوده مقادیر بر اساس نوع سنسور
- **Format Validation**: بررسی فرمت well_id و timestamp
- **Quality Score**: محاسبه نمره کیفیت داده (0-100)

### Sensor Ranges
```python
{
    'motor_temperature': {'min': 65, 'max': 120, 'unit': 'C'},
    'intake_pressure': {'min': 450, 'max': 600, 'unit': 'psi'},
    'discharge_pressure': {'min': 800, 'max': 1200, 'unit': 'psi'},
    'vibration': {'min': 0.5, 'max': 5.0, 'unit': 'g'},
    'current': {'min': 30, 'max': 80, 'unit': 'A'},
    'flow_rate': {'min': 1500, 'max': 2500, 'unit': 'bpd'},
}
```

## Kafka Integration

تمام داده‌های validated به Kafka ارسال می‌شوند:

- **Topic**: `sensor-data` (قابل تنظیم)
- **Key**: well_id یا node_id
- **Format**: JSON
- **Compression**: gzip

## Statistics

برای مشاهده آمار ingestion:

```bash
curl -X GET "http://localhost:8000/api/v1/ingestion/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "total_received": 1000,
  "total_validated": 950,
  "total_sent_to_kafka": 950,
  "total_errors": 50,
  "sources": {
    "mqtt": 600,
    "opcua": 300,
    "rest": 100
  },
  "is_running": true,
  "mqtt_connected": true,
  "opcua_connected": true
}
```

## API Endpoints

### POST `/api/v1/ingestion/sensor`
Ingest single sensor reading

### POST `/api/v1/ingestion/sensor/batch`
Ingest batch of sensor readings (max 1000)

### POST `/api/v1/ingestion/raw`
Ingest raw data in any format

### GET `/api/v1/ingestion/stats`
Get ingestion statistics

## پیکربندی

در فایل `.env`:
```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_SENSOR_DATA=sensor-data

# MQTT (optional)
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# OPC-UA (optional)
OPCUA_ENDPOINT_URL=opc.tcp://localhost:4840/freeopcua/server/
```

## Troubleshooting

### MQTT Connection Failed
- بررسی کنید MQTT broker در حال اجرا باشد
- بررسی firewall و port 1883
- بررسی credentials

### OPC-UA Connection Failed
- بررسی کنید OPC-UA server در حال اجرا باشد
- بررسی endpoint URL
- بررسی Node IDs

### Kafka Send Failed
- بررسی کنید Kafka broker در حال اجرا باشد
- بررسی connection string
- بررسی topic وجود دارد

## Best Practices

1. **Batch Processing**: برای داده‌های زیاد از batch endpoint استفاده کنید
2. **Error Handling**: همیشه response را بررسی کنید
3. **Monitoring**: آمار ingestion را به صورت منظم بررسی کنید
4. **Validation**: داده‌ها را قبل از ارسال validate کنید
5. **Retry Logic**: در صورت خطا، retry کنید

