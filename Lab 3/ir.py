import network
import time
from machine import Pin
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Seng Sophea 01"
WIFI_PASS = "369369369"

BLYNK_TOKEN = "tlTO6V8rLVLOPaESRh90TEWAKgzp7wbQ"
BLYNK_API   = "https://blynk.cloud/external/api"
#define BLYNK_TEMPLATE_NAME "IR Gate Monitor"
#define BLYNK_AUTH_TOKEN "tlTO6V8rLVLOPaESRh90TEWAKgzp7wbQ"
IR_PIN = 12

# ---------- HARDWARE ----------
ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi connected:", wifi.ifconfig())

# ---------- SEND IR STATUS ----------
def send_ir_status(text):
    text = text.replace(" ", "%20")  # encode spaces manually
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={text}"
    try:
        r = requests.get(url)
        r.close()
        print("IR status sent:", text)
    except Exception as e:
        print("Blynk error:", e)

# ---------- MAIN ----------
print("Running IR sensor monitoring...")

last_text = ""

while True:
    text = "Obstacle Detected" if ir.value() == 0 else "Not Detected"
    
    if text != last_text:
        print(text)
        send_ir_status(text)
        last_text = text

    time.sleep(1)
