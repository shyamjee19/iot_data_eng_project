from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime


def extract_data():
    print("Extracting telemetry data")


def transform_data():
    print("Transforming telemetry data")


def load_data():
    print("Loading telemetry data")


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