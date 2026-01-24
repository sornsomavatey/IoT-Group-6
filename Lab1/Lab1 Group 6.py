import network
import urequests
import time
from machine import Pin
import dht

# ======================
# WIFI
# ======================
SSID = "IoT"
PASSWORD = "90407833"

# ======================
# TELEGRAM
# ======================
BOT_TOKEN = "8535506703:AAFONc38bFBpwWEGOcN63rEgjKH5KVKeutM"
CHAT_ID = -5215104154

SEND_URL = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
GET_URL  = "https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN)

# ======================
# HARDWARE
# ======================
sensor = dht.DHT11(Pin(33))
relay = Pin(15, Pin.OUT)
relay.off()

# ======================
# STATE
# ======================
last_update_id = 0
auto_off_sent = False

# ======================
# WIFI SETUP
# ======================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# ======================
# WIFI AUTO RECONNECT
# ======================
def wifi_connect():
    if not wifi.isconnected():
        print("WiFi lost — reconnecting")
        wifi.disconnect()
        wifi.connect(SSID, PASSWORD)

        t = 10
        while not wifi.isconnected() and t > 0:
            time.sleep(1)
            t -= 1

        if wifi.isconnected():
            print("WiFi reconnected")
        else:
            print("WiFi reconnect failed")

# ======================
# TELEGRAM SEND
# ======================
def send_message(text):
    try:
        text = text.replace(" ", "%20")
        payload = "chat_id={}&text={}".format(CHAT_ID, text)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        r = urequests.post(SEND_URL, data=payload, headers=headers)

        if r.status_code != 200:
            print("Telegram HTTP error:", r.status_code)
            r.close()
            return False

        r.close()
        return True

    except Exception as e:
        print("Telegram error:", e)
        return False

# ======================
# MAIN LOOP (5s)
# ======================
while True:

    wifi_connect()

    # ---------- SENSOR ----------
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("Temp:", temp, "Hum:", hum)
    except OSError:
        print("DHT error — skipping cycle")
        time.sleep(5)
        continue

    # ---------- TASK 4 LOGIC ----------
    if temp >= 30 and relay.value() == 0:
        send_message("ALERT!\nTemp {:.2f} C\nRelay OFF".format(temp))
        auto_off_sent = False

    if temp < 30 and relay.value() == 1:
        relay.off()
        if not auto_off_sent:
            send_message("Temperature normal\nRelay auto-OFF")
            auto_off_sent = True

    # ---------- TELEGRAM COMMANDS ----------
    try:
        url = GET_URL + "?offset={}".format(last_update_id + 1)
        r = urequests.get(url)

        if r.status_code != 200:
            print("Telegram GET error:", r.status_code)
            r.close()
            time.sleep(5)
            continue

        data = r.json()
        r.close()

        for update in data["result"]:
            last_update_id = update["update_id"]
            msg = update.get("message")

            if not msg:
                continue

            if msg["chat"]["id"] != CHAT_ID:
                continue

            text = msg.get("text", "")

            if text == "/on":
                relay.on()
                send_message("Relay turned ON")

            elif text == "/off":
                relay.off()
                send_message("Relay turned OFF")

            elif text == "/status":
                state = "ON" if relay.value() else "OFF"
                send_message(
                    "Temp: {:.2f} C\nHum: {:.2f} %\nRelay: {}".format(
                        temp, hum, state
                    )
                )

    except Exception as e:
        print("Telegram loop error:", e)

    time.sleep(5)

