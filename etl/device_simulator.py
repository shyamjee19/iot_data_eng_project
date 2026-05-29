import sys
import os
import random
import time
import json
from datetime import datetime

import paho.mqtt.client as mqtt

# Add project root directory to path to enable settings import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs import settings

client = mqtt.Client()

print(f"Connecting to MQTT Broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}...")
client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)


devices = [
    "motor-01",
    "motor-02",
    "pump-01"
]

while True:

    data = {
        "device_id": random.choice(devices),
        "temperature": round(random.uniform(20, 100), 2),
        "vibration": round(random.uniform(0.1, 1.0), 2),
        "pressure": round(random.uniform(90, 120), 2),
        "event_time": str(datetime.now())
    }

    client.publish(
        settings.MQTT_TOPIC,
        json.dumps(data)
    )

    print("Published:", data)

    time.sleep(2)