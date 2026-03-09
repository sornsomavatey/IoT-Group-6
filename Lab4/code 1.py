import network
import time
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, ADC

# WiFi
SSID = "CINNAMON CAFE & BISTRO"
PASSWORD = "cinnamoncafe"

# MQTT
BROKER = "192.168.1.111"
PORT = 1883
CLIENT_ID = b"from_esp32_1"
TOPIC = b"/lab4/task1"
KEEPALIVE = 30

# ---------- WIFI ----------
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep(0.5)

    print("WiFi Connected:", wlan.ifconfig())


# ---------- MQTT ----------
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER, PORT, keepalive=KEEPALIVE)
    client.connect()
    print("MQTT Connected")
    return client


# ---------- MQ5 SETUP ----------
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)      # 0 - 3.3V
mq5.width(ADC.WIDTH_12BIT)    # 0 - 4095

# Store last 5 readings
readings = []


# ---------- MAIN ----------
def main():
    wifi_connect()
    client = connect_mqtt()

    while True:

        # Read sensor
        raw = mq5.read()

        # Store reading
        readings.append(raw)

        if len(readings) > 5:
            readings.pop(0)

        # Moving average
        avg = sum(readings) / len(readings)

        # Voltage calculation (optional debug)
        voltage = (raw / 4095) * 3.3

        # Debug terminal output
        print("Raw:", raw)
        print("Average:", round(avg, 2))
        print("Voltage:", round(voltage, 2), "V")
        print("----------------------")

        # Data for Node-RED
        data = {
            "raw": raw,
            "average": round(avg, 2),
            "voltage": round(voltage, 2)
        }

        msg = ujson.dumps(data)

        try:
            client.publish(TOPIC, msg)
            print("MQTT Sent:", msg)
        except:
            print("MQTT publish failed")

        time.sleep(2)


main()
