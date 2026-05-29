import sys
import os
import json

import paho.mqtt.client as mqtt
from kafka import KafkaProducer

# Add project root directory to path to enable settings import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs import settings

print(f"Initializing Kafka Producer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}...")
producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(client, userdata, message):

    try:
        payload = json.loads(message.payload.decode())

        producer.send(
            settings.KAFKA_TOPIC,
            payload
        )

        print("Sent to Kafka:", payload)
    except Exception as e:
        print("Error processing message:", e)

client = mqtt.Client()

client.on_message = on_message

print(f"Connecting to MQTT Broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}...")
client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)

client.subscribe(settings.MQTT_TOPIC)

print(f"MQTT to Kafka Bridge active. Subscribed to MQTT: '{settings.MQTT_TOPIC}' -> Kafka: '{settings.KAFKA_TOPIC}'...")

client.loop_forever()