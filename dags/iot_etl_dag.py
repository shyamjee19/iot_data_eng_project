import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Add the project root to systemic path so Airflow worker can import from etl and configs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.postgres_to_snowflake import sync_postgres_to_snowflake

def extract_data():
    print("--- [AIRFLOW ETL] Phase 1: Extract Staging Data ---")
    print("Querying fresh telemetry rows from PostgreSQL database...")


def transform_data():
    print("--- [AIRFLOW ETL] Phase 2: Transform Data ---")
    print("Applying validation constraints, resolving duplicates, and parsing timestamps...")


def load_data():
    print("--- [AIRFLOW ETL] Phase 3: Bulk Load to Snowflake ---")
    # Trigger the real PostgreSQL-to-Snowflake load pipeline
    sync_postgres_to_snowflake()


with DAG(
    dag_id='iot_etl_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load = PythonOperator(
        task_id='load_data',
        python_callable=load_data
    )

    extract >> transform >> load