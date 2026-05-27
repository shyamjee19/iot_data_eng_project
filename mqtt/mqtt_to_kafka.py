import json

import paho.mqtt.client as mqtt

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['127.0.0.1:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(client, userdata, message):

    payload = json.loads(message.payload.decode())

    producer.send(
        'iot-telemetry',
        payload
    )

    print("Sent to Kafka:", payload)

client = mqtt.Client()

client.on_message = on_message

client.connect("localhost", 1883, 60)

client.subscribe("iot/telemetry")

print("MQTT to Kafka started...")

client.loop_forever()