from machine import Pin
import time
from tm1637 import TM1637
import urequests as requests
import network


WIFI_SSID = "IoT"
WIFI_PASS = "90407833"

# Setup WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

if not wifi.isconnected():
    print("Connecting to WiFi...")
    wifi.connect(WIFI_SSID, WIFI_PASS)
    while not wifi.isconnected():
        time.sleep(1)

print("WiFi connected:", wifi.ifconfig())


# ---------- CONFIG ----------
IR_PIN = 12
CLK_PIN = 17
DIO_PIN = 16

BLYNK_TOKEN = "To2jHWZWs_tH7H7YIXrIbxE8RPHilz34"
BLYNK_API = "https://blynk.cloud/external/api"
BLYNK_PIN = "V1"  # virtual pin to push counter

DEBOUNCE_MS = 200  # minimum time between counts

# ---------- HARDWARE ----------
ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)
tm = TM1637(clk_pin=CLK_PIN, dio_pin=DIO_PIN, brightness=5)

# ---------- VARIABLES ----------
counter = 0
last_ir_state = 1
last_detect_time = 0

# ---------- FUNCTIONS ----------
def update_display(value):
    """Show counter on TM1637"""
    tm.show_number(value)

def push_to_blynk(value, retries=3):
    """Send counter to Blynk with retry (no urllib needed)"""
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&pin={BLYNK_PIN}&value={value}"
    
    for attempt in range(retries):
        try:
            r = requests.get(url)
            r.close()
            print("Pushed to Blynk:", value)
            return
        except Exception as e:
            print(f"Blynk push error (attempt {attempt+1}):", e)
            time.sleep(0.2)


# ---------- MAIN LOOP ----------
while True:
    ir_state = ir.value()
    current_time = time.ticks_ms()
    
    # Count new detection: no object -> object
    if ir_state == 0 and last_ir_state == 1:
        if time.ticks_diff(current_time, last_detect_time) > DEBOUNCE_MS:
            counter += 1
            print("Object detected! Count:", counter)
            update_display(counter)
            push_to_blynk(counter)
            last_detect_time = current_time

    last_ir_state = ir_state
    time.sleep(0.05)
