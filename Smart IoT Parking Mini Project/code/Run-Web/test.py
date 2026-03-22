import os
import time
from services.blynk_client import BlynkClient

BLYNK_TOKEN = os.getenv("BLYNK_TOKEN", "56q-xORQx9rKec76e3-UnXFi-zL-8y3-")
blynk = BlynkClient(BLYNK_TOKEN)

print("Blynk client initialized. Waiting for commands...")

while True:
    try:
        commands = blynk.get_commands()  # <-- adjust based on your BlynkClient API
        if commands:
            print("Commands received:", commands)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)