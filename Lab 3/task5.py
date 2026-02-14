from machine import Pin, PWM
import time
from tm1637 import TM1637
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "IoT"
WIFI_PASS = "90407833"

IR_PIN = 12
SERVO_PIN = 13
CLK_PIN = 17
DIO_PIN = 16

BLYNK_TOKEN = "eoMbl5noCIyKWg-QYZ00hGEjXppvQGBX"
BLYNK_API = "https://blynk.cloud/external/api"

V_IR_STATUS = "V0"   # Obstacle detected / Not detected
V_SERVO = "V1"       # Servo slider 0-180
V_COUNTER = "V2"     # IR detection count
V_MANUAL = "V3"      # Manual override switch

DEBOUNCE_MS = 200
SERVO_OPEN_ANGLE = 90
SERVO_CLOSED_ANGLE = 0

# ---------- HARDWARE ----------
ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(SERVO_PIN), freq=50)
tm = TM1637(clk_pin=CLK_PIN, dio_pin=DIO_PIN, brightness=5)

# ---------- VARIABLES ----------
counter = 0
last_ir_state = 1
last_detect_time = 0
manual_override = 0
servo_open = False
last_servo_angle = -1

# ---------- FUNCTIONS ----------
def connect_wifi():
    import network
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.connect(WIFI_SSID, WIFI_PASS)
        while not wifi.isconnected():
            time.sleep(1)
    print("WiFi connected:", wifi.ifconfig())

def set_servo_angle(angle):
    """Map 0-180° to PWM duty"""
    min_duty = 26   # 0° ~ 0.5ms
    max_duty = 128  # 180° ~ 2.5ms
    duty = int(min_duty + (angle/180)*(max_duty-min_duty))
    servo.duty(duty)

def push_to_blynk(value, pin, retries=3):
    """Send value to Blynk virtual pin"""
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&{pin}={value}"
    for attempt in range(retries):
        try:
            r = requests.get(url)
            r.close()
            return
        except Exception as e:
            print(f"Blynk push error (attempt {attempt+1}):", e)
            time.sleep(0.2)

def read_blynk_pin(pin):
    """Read value from Blynk virtual pin"""
    try:
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&{pin}"
        r = requests.get(url)
        value = int(str(r.text).strip("[]"))
        r.close()
        return value
    except Exception as e:
        print("Blynk read error:", e)
        return None

def update_display(value):
    tm.show_number(value)

# ---------- MAIN ----------
connect_wifi()
print("Starting ESP32 Tasks 1-5...")

while True:
    # --- Read manual override ---
    val = read_blynk_pin(V_MANUAL)
    if val is not None:
        manual_override = val

    # --- Read IR sensor ---
    ir_state = ir.value()
    current_time = time.ticks_ms()

    # --- Automatic IR actions if manual_override off ---
    if manual_override == 0:
        # Count new detection
        if ir_state == 0 and last_ir_state == 1:
            if time.ticks_diff(current_time, last_detect_time) > DEBOUNCE_MS:
                counter += 1
                last_detect_time = current_time
                print("Object detected! Count:", counter)
                update_display(counter)
                push_to_blynk(counter, V_COUNTER)

        # Servo automatic open/close
        if ir_state == 0 and not servo_open:
            set_servo_angle(SERVO_OPEN_ANGLE)
            servo_open = True
        elif ir_state == 1 and servo_open:
            time.sleep(1)  # keep open 1 second
            set_servo_angle(SERVO_CLOSED_ANGLE)
            servo_open = False

        # Push IR status to Blynk
        ir_text = "Obstacle detected" if ir_state == 0 else "Not detected"
        push_to_blynk(ir_text.replace(" ", "%20"), V_IR_STATUS)

    else:
        # Manual mode: ignore IR
        print("Manual override active — IR ignored")

    last_ir_state = ir_state

    # --- Servo manual control via slider ---
    angle = read_blynk_pin(V_SERVO)
    if angle is not None and angle != last_servo_angle:
        set_servo_angle(angle)
        last_servo_angle = angle

    time.sleep(0.05)
