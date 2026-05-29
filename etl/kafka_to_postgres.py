import sys
import os
import json

from kafka import KafkaConsumer
import psycopg2

# Add project root directory to path to enable settings import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs import settings

print(f"Initializing Kafka Consumer for topic '{settings.KAFKA_TOPIC}' connected to {settings.KAFKA_BOOTSTRAP_SERVERS}...")
consumer = KafkaConsumer(
    settings.KAFKA_TOPIC,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print(f"Connecting to PostgreSQL database '{settings.PG_DATABASE}' at {settings.PG_HOST}:{settings.PG_PORT}...")
connection = psycopg2.connect(
    host=settings.PG_HOST,
    database=settings.PG_DATABASE,
    user=settings.PG_USER,
    password=settings.PG_PASSWORD,
    port=settings.PG_PORT
)

cursor = connection.cursor()

cursor.execute("SELECT current_database();")
print("Connected to PostgreSQL Database:", cursor.fetchone()[0])

print("Awaiting messages from Kafka...")

for message in consumer:

    data = message.value

    print("Received:", data)

    insert_query = """
    INSERT INTO telemetry_data
    (
        device_id,
        temperature,
        vibration,
        pressure,
        event_time
    )
    VALUES (%s,%s,%s,%s,%s)
    """

    try:

        cursor.execute(
            insert_query,
            (
                data['device_id'],
                data['temperature'],
                data['vibration'],
                data['pressure'],
                data['event_time']
            )
        )

        connection.commit()

        print("Successfully Inserted:", data)

    except Exception as e:

        print("Insertion ERROR:", e)

        connection.rollback()