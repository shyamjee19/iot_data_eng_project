import json

from kafka import KafkaConsumer

import psycopg2

consumer = KafkaConsumer(
    'iot-telemetry',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

connection = psycopg2.connect(
    host="localhost",
    database="iot_db",
    user="admin",
    password="admin123",
    port="5432"
)

cursor = connection.cursor()

cursor.execute("SELECT current_database();")
print(cursor.fetchone())

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

        print("Inserted:", data)

    except Exception as e:

        print("ERROR:", e)

        connection.rollback()