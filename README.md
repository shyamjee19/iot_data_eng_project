# 🏭 End-to-End Industrial IoT Data Engineering Pipeline

A premium, state-of-the-art real-time streaming and batch orchestration pipeline. This project simulates industrial IoT devices, streams telemetry data over MQTT and Kafka brokers, ingests real-time inputs into PostgreSQL and Apache Spark Structured Streaming, syncs aggregated events into a Snowflake Cloud Data Warehouse using Apache Airflow, and feeds dashboards for real-time operations.

---

## 📐 Pipeline Architecture

```
[IoT Devices] ➔ [Eclipse Mosquitto MQTT] ➔ [MQTT-Kafka Bridge] ➔ [Apache Kafka Broker]
                                                                        │
       ┌────────────────────────────────────────────────────────────────┘
       ▼                                                                ▼
[Python Consumer]                                           [Apache Spark Streaming]
       │                                                                │
       ▼ (Real-Time Ingest)                                             ▼ (Real-Time Analysis)
[PostgreSQL Database]                                              [Console Output]
       │
       ▼ (Airflow Orchestrated ELT Sync)
[Snowflake Cloud Data Warehouse] ➔ [Power BI Dashboard]
```

---

## 📂 Project Directory Structure

```
data-engineering-project/
├── dags/
│   └── iot_etl_dag.py            # Airflow DAG for PostgreSQL-to-Snowflake sync
├── etl/
│   ├── device_simulator.py       # Simulates motor/pump parameters over MQTT
│   ├── mqtt_to_kafka.py          # Bridges MQTT events over to Kafka streams
│   ├── kafka_to_postgres.py      # Real-time Kafka consumer writing to PostgreSQL
│   ├── spark_streaming.py        # Structured PySpark schema-parsed consumer
│   └── postgres_to_snowflake.py  # Bulk loading sync from PostgreSQL to Snowflake
├── sql/
│   └── schema.sql                # PostgreSQL table and indexing scripts
├── configs/
│   └── settings.py               # Central settings and environment config
├── docker/                       # Dockerfiles and container configurations
├── logs/                         # Execution logs
├── data/                         # Local data volume mounts
├── dashboards/                   # Power BI mockups and config parameters
├── docker-compose.yml            # Core dockerized services (Kafka, MQTT, Postgres)
├── requirements.txt              # Pipeline dependencies manifest
└── README.md                     # High-quality technical guide (This file)
```

---

## 🚀 Setup & Run Instructions

Follow these step-by-step instructions to boot up and run the entire telemetry ingestion flow:

### Step 1: Install Dependencies
Create a Python virtual environment and install the required modules:
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

### Step 2: Spin Up Infrastructure Containers
Use Docker Compose to spin up the PostgreSQL database, Eclipse Mosquitto MQTT Broker, Zookeeper, and the Apache Kafka broker:
```bash
docker-compose up -d
```
*Verify containers are running with `docker ps`.*

### Step 3: Initialize PostgreSQL Schema
Execute the SQL creation script to establish the `telemetry_data` table in the database:
```bash
# Using standard psql inside postgres container:
docker exec -i iot-postgres psql -U admin -d iot_db < sql/schema.sql
```

### Step 4: Configure Settings & Credentials
Edit `configs/settings.py` or export environment variables to customize connection strings:
```python
# To enable active cloud synchronization, add your Snowflake credentials:
SNOWFLAKE_USER = "YOUR_USER"
SNOWFLAKE_PASSWORD = "YOUR_PASSWORD"
SNOWFLAKE_ACCOUNT = "YOUR_ACCOUNT"
```

### Step 5: Start the Streaming Services
Run each service in a separate terminal window (ensure your virtual environment is active in each):

1. **Start the MQTT-to-Kafka Broker Bridge**:
   ```bash
   python etl/mqtt_to_kafka.py
   ```
2. **Start the Database Consumer** (Ingests Kafka topics into PostgreSQL):
   ```bash
   python etl/kafka_to_postgres.py
   ```
3. **Start the Spark Structured Streaming Pipeline**:
   ```bash
   python etl/spark_streaming.py
   ```
4. **Trigger the IoT Device Simulator**:
   ```bash
   python etl/device_simulator.py
   ```

---

## ❄️ PostgreSQL & Snowflake ELT Orchestration

Staging data is stored in high-performance PostgreSQL tables. Apache Airflow (`dags/iot_etl_dag.py`) triggers a daily cron job that aggregates operational inputs and launches `etl/postgres_to_snowflake.py`. 

* If Snowflake credentials are omitted, the script automatically defaults to a **Mock-Sync Mode**, querying PostgreSQL counts, validating formatting, and outputting execution logs to allow sandbox testing without third-party accounts.
* Once Snowflake credentials are provided, the script builds target time-series tables in your Snowflake data schema and bulk syncs data using high-speed transactional inserts.

---

## 📊 Analytics Dashboard

The `dashboards/` directory is reserved for visualizing processed Snowflake and PostgreSQL tables. Telemetry parameters track critical operational limits:
* **Motor Failures**: Correlate high temperatures (>80°C) with abnormal vibration readings (>0.8 mm/s).
* **Pressure Transients**: Trend line tracking pressure drift in `pump-01` over time.
