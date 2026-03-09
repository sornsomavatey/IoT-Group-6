import network
import time
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, ADC

# WiFi
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# MQTT
BROKER = "10.30.0.172"
PORT = 1883
CLIENT_ID = b"esp32_mq5_1"
TOPIC = b"/aupp/esp32/mq5"
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

    print("WiFi OK:", wlan.ifconfig())


# ---------- MQTT ----------
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER, PORT, keepalive=KEEPALIVE)
    client.connect()
    print("MQTT Connected")
    return client


# ---------- MQ5 ----------
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

readings = []


# ---------- RISK CLASSIFICATION ----------
def classify_risk(value):

    if value < 2100:
        return "SAFE"

    elif value < 2600:
        return "WARNING"

    else:
        return "DANGER"


# ---------- MAIN ----------
def main():

    wifi_connect()
    client = connect_mqtt()

    while True:

        raw = mq5.read()

        readings.append(raw)
        if len(readings) > 5:
            readings.pop(0)

        avg = sum(readings) / len(readings)

        voltage = (raw / 4095) * 3.3

        # Risk classification
        risk = classify_risk(avg)

        # -------- Terminal Debug --------
        print("Raw:", raw)
        print("Average:", round(avg,2))
        print("Voltage:", round(voltage,2), "V")
        print("Risk Level:", risk)
        print("------------------------")

        # Data to send
        data = {
            "raw": raw,
            "average": round(avg,2),
            "voltage": round(voltage,2),
            "risk_level": risk
        }

        msg = ujson.dumps(data)

        try:
            client.publish(TOPIC, msg)
            print("MQTT Sent:", msg)
        except:
            print("MQTT publish failed")

        time.sleep(2)


main()