import network
import socket
import time
from machine import Pin, I2C, PWM
import neopixel
from tcs34527 import TCS34725

# ---------------- WIFI ----------------
WIFI_SSID = "IoT"
WIFI_PASSWORD = "90407833"

# ---------------- SENSOR ----------------
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
sensor = TCS34725(i2c)

# ---------------- NEOPIXEL ----------------
NUM_LEDS = 16
led = neopixel.NeoPixel(Pin(23), NUM_LEDS)

# ---------------- MOTOR ----------------
ena = PWM(Pin(14))
ena.freq(1000)

in1 = Pin(26, Pin.OUT)
in2 = Pin(27, Pin.OUT)

# ---------------- COLOR REFERENCES ----------------
RED_REF = (411, 104, 87)
GREEN_REF = (53, 49, 36)
BLUE_REF = (277, 282, 237)

# ---------------- STATES ----------------
current_color = "UNKNOWN"

manual_led_mode = False
manual_rgb = (0, 0, 0)

manual_motor_mode = False
motor_state = "STOP"
pending_motor_command = None

# ---------------- HELPERS ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        print("Connecting to WiFi", end="")
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)

    print("\nWiFi connected")
    print("IP address:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def read_avg(samples=10, delay=0.05):
    tr = tg = tb = tc = 0
    for _ in range(samples):
        r, g, b, c = sensor.read_raw()
        tr += r
        tg += g
        tb += b
        tc += c
        time.sleep(delay)
    return tr // samples, tg // samples, tb // samples, tc // samples

def normalize_rgb(r, g, b):
    total = r + g + b
    if total == 0:
        return (0, 0, 0)
    return (r / total, g / total, b / total)

def distance(c1, c2):
    return (
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )

RED_N = normalize_rgb(*RED_REF)
GREEN_N = normalize_rgb(*GREEN_REF)
BLUE_N = normalize_rgb(*BLUE_REF)

def classify_color(r, g, b):
    current = normalize_rgb(r, g, b)

    d_red = distance(current, RED_N)
    d_green = distance(current, GREEN_N)
    d_blue = distance(current, BLUE_N)

    if d_red <= d_green and d_red <= d_blue:
        return "RED"
    elif d_green <= d_red and d_green <= d_blue:
        return "GREEN"
    else:
        return "BLUE"

def clear_led():
    for i in range(NUM_LEDS):
        led[i] = (0, 0, 0)
    led.write()

def show_auto_color(color):
    clear_led()
    if color == "RED":
        led[0] = (255, 0, 0)
    elif color == "GREEN":
        led[0] = (0, 255, 0)
    elif color == "BLUE":
        led[0] = (0, 0, 255)
    led.write()

def show_manual_rgb(r, g, b):
    clear_led()
    led[0] = (r, g, b)
    led.write()

def motor_forward(duty=700):
    global motor_state
    in1.value(1)
    in2.value(0)
    ena.duty(duty)
    motor_state = "FORWARD"
    print("Motor FORWARD duty =", duty)

def motor_backward(duty=700):
    global motor_state
    in1.value(0)
    in2.value(1)
    ena.duty(duty)
    motor_state = "BACKWARD"
    print("Motor BACKWARD duty =", duty)

def motor_stop():
    global motor_state
    ena.duty(0)
    in1.value(0)
    in2.value(0)
    motor_state = "STOP"
    print("Motor STOP")

def set_motor_speed_by_color(color):
    if color == "RED":
        motor_forward(800)
    elif color == "GREEN":
        motor_forward(600)
    elif color == "BLUE":
        motor_forward(400)
    else:
        motor_stop()

def parse_query(path):
    params = {}
    if "?" not in path:
        return params

    query = path.split("?", 1)[1]
    for pair in query.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = v
    return params

def make_response(body, content_type="text/plain", status="200 OK"):
    return (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n\r\n"
        "{}"
    ).format(status, content_type, body)

def status_json():
    return (
        '{{'
        '"color":"{}",'
        '"manual_led_mode":{},'
        '"manual_motor_mode":{},'
        '"motor_state":"{}",'
        '"r":{},'
        '"g":{},'
        '"b":{}'
        '}}'
    ).format(
        current_color,
        "true" if manual_led_mode else "false",
        "true" if manual_motor_mode else "false",
        motor_state,
        manual_rgb[0],
        manual_rgb[1],
        manual_rgb[2]
    )

def handle_request(path):
    global manual_led_mode, manual_motor_mode, manual_rgb, pending_motor_command

    if path.startswith("/status"):
        return make_response(status_json(), "application/json")

    elif path.startswith("/forward"):
        manual_motor_mode = True
        pending_motor_command = ("forward", 800)
        return make_response("FORWARD")

    elif path.startswith("/backward"):
        manual_motor_mode = True
        pending_motor_command = ("backward", 800)
        return make_response("BACKWARD")

    elif path.startswith("/stop"):
        manual_motor_mode = False
        pending_motor_command = ("stop", 0)
        return make_response("STOP")

    elif path.startswith("/auto"):
        manual_led_mode = False
        manual_motor_mode = False
        pending_motor_command = None
        show_auto_color(current_color)
        set_motor_speed_by_color(current_color)
        return make_response("AUTO_MODE")

    elif path.startswith("/set_rgb"):
        params = parse_query(path)
        try:
            r = int(params.get("r", 0))
            g = int(params.get("g", 0))
            b = int(params.get("b", 0))

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            manual_rgb = (r, g, b)
            manual_led_mode = True
            show_manual_rgb(r, g, b)

            return make_response("RGB_SET")
        except Exception as e:
            print("RGB error:", e)
            return make_response("INVALID_RGB", "text/plain", "400 Bad Request")

    else:
        return make_response("ESP32 OK")

def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    s.settimeout(0.2)
    print("Server running on port 80")
    return s

# ---------------- MAIN ----------------
ip = connect_wifi()
server = start_server()

last_sensor_update = 0

while True:
    now = time.ticks_ms()

    # 1) sensor / auto logic
    if time.ticks_diff(now, last_sensor_update) > 1000:
        last_sensor_update = now
        try:
            r, g, b, c = read_avg()

            if c > 0:
                current_color = classify_color(r, g, b)
                print("R:", r, "G:", g, "B:", b, "C:", c, "=>", current_color)

                if not manual_led_mode:
                    show_auto_color(current_color)

                if not manual_motor_mode:
                    set_motor_speed_by_color(current_color)

        except Exception as e:
            print("Sensor error:", e)

    # 2) execute pending manual motor command
    if pending_motor_command is not None:
        cmd, duty = pending_motor_command
        pending_motor_command = None

        try:
            if cmd == "forward":
                motor_forward(duty)
            elif cmd == "backward":
                motor_backward(duty)
            elif cmd == "stop":
                motor_stop()
        except Exception as e:
            print("Motor command error:", e)

    # 3) web server
    try:
        conn, addr = server.accept()
        request = conn.recv(1024)

        if not request:
            conn.close()
            continue

        request = request.decode()
        first_line = request.split("\r\n")[0]
        parts = first_line.split(" ")

        path = "/"
        if len(parts) >= 2:
            path = parts[1]

        print("Request:", path)

        response = handle_request(path)
        conn.send(response)
        conn.close()

    except OSError:
        pass
    except Exception as e:
        print("Server error:", e)