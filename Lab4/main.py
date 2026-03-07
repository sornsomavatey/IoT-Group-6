import network
import time
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, ADC, I2C
import mlx90614
import bmp280
import time
import ds3231
# WiFi
SSID = "IoT"
PASSWORD = "90407833"

# MQTT
BROKER = "192.168.0.7"
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

def classify_risk(value):

    if value < 2100:
        return "SAFE"

    elif value < 2600:
        return "WARNING"

    else:
        return "DANGER"


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
# ---------- MLX90614 ----------
mlx_sensor = mlx90614.MLX90614(i2c)
# ---------- BMP280 Setup ----------
bmp_sensor = bmp280.BMP280(i2c)
# DS3231
rtc = ds3231.DS3231(i2c)
# ---------- FEVER DETECTION ----------
def fever_detection(body_temp):
    return 1 if body_temp >= 32.5 else 0

# ---------- MAIN ----------
def main():
    wifi_connect()
    client = connect_mqtt()

    while True:
        # --- MQ-5 Gas ---
        raw = mq5.read()
        readings.append(raw)
        if len(readings) > 5:
            readings.pop(0)
        avg = sum(readings) / len(readings)
        voltage = (raw / 4095) * 3.3
        risk = classify_risk(avg)

        # --- MLX90614 ---
        ambient_temp = mlx_sensor.read_ambient_temp()
        body_temp = mlx_sensor.read_object_temp()
        fever_flag = fever_detection(body_temp)

        # --- BMP280 ---
        bmp_temp = bmp_sensor.temperature
        bmp_pressure = bmp_sensor.pressure / 100   # hPa
        bmp_altitude = bmp_sensor.altitude

        # --- DS3231 RTC ---
        now = rtc.get_time()  # (year, month, day, hour, minute, second)
        date_str = "{}-{:02}-{:02}".format(now[0], now[1], now[2])
        time_str = "{:02}:{:02}:{:02}".format(now[3], now[4], now[5])

        # --- Debug Print ---
        print("Date:", date_str, "Time:", time_str)

        print("MQ-5 -> Raw:", raw,
              "\nAvg:", round(avg,2),
              "\nV:", round(voltage,2),
              "\nRisk:", risk)

        print("MLX90614 -> Ambient:", round(ambient_temp,2),
              "\nBody:", round(body_temp,2),
              "\nFever:", fever_flag)

        print("BMP280 -> Temp:", round(bmp_temp,2),
              "\nPressure:", round(bmp_pressure,2),
              "\nAltitude:", round(bmp_altitude,2))

        print("----------------------------")

        # --- Combine all data for MQTT ---
        data = {
            "date": date_str,
            "time": time_str,
            "mq5_raw": raw,
            "mq5_avg": round(avg,2),
            "mq5_voltage": round(voltage,2),
            "risk_level": risk,
            "ambient_temp": round(ambient_temp,2),
            "body_temp": round(body_temp,2),
            "fever_flag": fever_flag,
            "bmp_temp": round(bmp_temp,2),
            "bmp_pressure": round(bmp_pressure,2),
            "bmp_altitude": round(bmp_altitude,2)
        }

        # --- MQTT Publish ---
        msg = ujson.dumps(data)
        try:
            client.publish(TOPIC, msg)
            print("MQTT Sent:", msg)
        except:
            print("MQTT publish failed")

        time.sleep(2)
        
main()


