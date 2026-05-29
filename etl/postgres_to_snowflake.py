# postgres_to_snowflake.py
# ELT Sync Script Orchestrated by Airflow

import sys
import os
import psycopg2

# Add project root directory to path to enable settings import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs import settings

def sync_postgres_to_snowflake():
    """
    Syncs telemetry data from PostgreSQL staging to the Snowflake Data Warehouse.
    """
    print("--- Starting PostgreSQL to Snowflake Sync Job ---")

    # 1. Check if Snowflake credentials are set
    if "YOUR_SNOWFLAKE" in (settings.SNOWFLAKE_USER, settings.SNOWFLAKE_PASSWORD, settings.SNOWFLAKE_ACCOUNT):
        print("[WARNING] Snowflake credentials are not configured in configs/settings.py.")
        print("[INFO] Please edit configs/settings.py or set environment variables to enable active Snowflake sync.")
        print("[INFO] Running in Mock-Mode: Simulating extraction from PostgreSQL and load to Snowflake.")
        mock_sync()
        return

    # 2. Establish connections if configured
    try:
        import snowflake.connector
    except ImportError:
        print("[ERROR] 'snowflake-connector-python' is not installed.")
        print("[INFO] Please install it via: pip install snowflake-connector-python")
        print("[INFO] Falling back to Mock-Mode sync simulation.")
        mock_sync()
        return

    pg_conn = None
    sf_conn = None
    try:
        print(f"Connecting to PostgreSQL operational database: '{settings.PG_DATABASE}'...")
        pg_conn = psycopg2.connect(
            host=settings.PG_HOST,
            database=settings.PG_DATABASE,
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            port=settings.PG_PORT
        )
        pg_cursor = pg_conn.cursor()

        print("Fetching staging data from PostgreSQL...")
        pg_cursor.execute("SELECT id, device_id, temperature, vibration, pressure, event_time, inserted_at FROM telemetry_data;")
        rows = pg_cursor.fetchall()
        print(f"Retrieved {len(rows)} records from PostgreSQL staging table.")

        if not rows:
            print("No new data to synchronize. Terminating job successfully.")
            return

        print(f"Connecting to Snowflake Account: '{settings.SNOWFLAKE_ACCOUNT}'...")
        sf_conn = snowflake.connector.connect(
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            account=settings.SNOWFLAKE_ACCOUNT,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA
        )
        sf_cursor = sf_conn.cursor()

        print("Verifying target schema in Snowflake...")
        sf_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {settings.SNOWFLAKE_SCHEMA}.telemetry_data (
            id INT,
            device_id VARCHAR(50),
            temperature FLOAT,
            vibration FLOAT,
            pressure FLOAT,
            event_time TIMESTAMP,
            inserted_at TIMESTAMP
        );
        """)

        print("Inserting records into Snowflake...")
        # Prepare list of values for insertion
        insert_query = f"""
        INSERT INTO {settings.SNOWFLAKE_SCHEMA}.telemetry_data 
        (id, device_id, temperature, vibration, pressure, event_time, inserted_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        sf_cursor.executemany(insert_query, rows)
        sf_conn.commit()

        print(f"[SUCCESS] Successfully loaded {len(rows)} records into Snowflake table '{settings.SNOWFLAKE_SCHEMA}.telemetry_data'!")

    except Exception as e:
        print("[ERROR] Failure occurred during PostgreSQL-to-Snowflake sync:", e)
    finally:
        if pg_conn:
            pg_conn.close()
        if sf_conn:
            sf_conn.close()

def mock_sync():
    """
    Simulates database sync if credentials are not specified yet.
    """
    try:
        connection = psycopg2.connect(
            host=settings.PG_HOST,
            database=settings.PG_DATABASE,
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            port=settings.PG_PORT
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_data;")
        count = cursor.fetchone()[0]
        print(f"[MOCK-SYNC] Extracted {count} records from local PostgreSQL database.")
        print(f"[MOCK-SYNC] Simulating bulk COPY of {count} rows into Snowflake Warehouse '{settings.SNOWFLAKE_WAREHOUSE}'...")
        print("[MOCK-SYNC] Sync Simulation Completed Successfully.")
        connection.close()
    except Exception as e:
        print("[MOCK-SYNC] Unable to connect to local Postgres database. Ensure docker services are running:", e)

if __name__ == "__main__":
    sync_postgres_to_snowflake()
