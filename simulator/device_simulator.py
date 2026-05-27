import random
import time
import json
from datetime import datetime

import paho.mqtt.client as mqtt

client = mqtt.Client()

client.connect("localhost", 1883, 60)


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
        "iot/telemetry",
        json.dumps(data)
    )

    print(data)

    time.sleep(2)