import network
import time
from machine import Pin, PWM
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Maggie"
WIFI_PASS = "77778888"

BLYNK_TOKEN = "ydpoCKFeMUACX6rT21BA1llcy5O4kpoc"
BLYNK_API   = "https://blynk.cloud/external/api"

SERVO_PIN = 13  # GPIO connected to servo signal

# ---------- HARDWARE ----------
servo = PWM(Pin(SERVO_PIN), freq=50)  # 50Hz standard servo

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi connected:", wifi.ifconfig())

# ---------- HELPER FUNCTIONS ----------
def get_slider_value():
    """Get slider value from Blynk V1"""
    try:
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V1"
        r = requests.get(url)
        value = int(str(r.text).strip('[]"{}'))  # parse JSON array
        r.close()
        return value
    except Exception as e:
        print("Error reading slider:", e)
        return None

def set_servo_angle(angle):
    """Convert angle (0-180) to PWM duty and set servo"""
    min_duty = 26   # 0° pulse width ~0.5ms
    max_duty = 128  # 180° pulse width ~2.5ms
    duty = int(min_duty + (angle/180)*(max_duty-min_duty))
    servo.duty(duty)

# ---------- MAIN LOOP ----------
last_angle = -1

while True:
    angle = get_slider_value()
    if angle is not None and angle != last_angle:
        print("Servo angle:", angle)
        set_servo_angle(angle)
        last_angle = angle
    time.sleep(0.2)
