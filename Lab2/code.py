import network
import socket
from machine import Pin, time_pulse_us, I2C
import dht
import time
from machine_i2c_lcd import I2cLcd

# ---------- I2C LCD Setup ----------
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

# ---------- WiFi Setup ----------
ssid = "IoT"
password = "90407833"

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, password)
while not sta.isconnected():
    time.sleep(0.5)
print("Connected:", sta.ifconfig())

# ---------- Hardware ----------
led = Pin(2, Pin.OUT)
led.off()

dht_sensor = dht.DHT11(Pin(4))
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)
TRIG.value(0)

# ---------- Sensor Functions ----------
def read_dht11():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature(), dht_sensor.humidity()
    except:
        return None, None

def read_ultrasonic():
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    duration = time_pulse_us(ECHO, 1, 30000)
    if duration < 0:
        return "Out of range"
    distance = (duration * 0.0343) / 2
    return "{:.2f} cm".format(distance)

# ---------- URL Decode Helper ----------
def url_decode(s):
    if s is None:
        return ""
    s = s.replace('+', ' ')
    s = s.replace('%20', ' ')
    return ''.join([c if 32 <= ord(c) <= 126 else ' ' for c in s])

def parse_query(query):
    params = {}
    for kv in query.split('&'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            params[k] = v
    return params

# ---------- Web Page ----------
def web_page():
    return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Web Server Control</title>
    <style>
        body { font-family: Arial; background: #f9f9f9; margin:0; height:100vh;
               display:flex; justify-content:center; align-items:center; }
        .container-wrapper { width:100%; display:flex; justify-content:center; }
        .container { width:90%; max-width:1100px; background:#fff; padding:30px;
                     border-radius:15px; box-shadow:0 8px 20px rgba(0,0,0,0.1);
                     display:grid; grid-template-columns:1fr 1fr 1fr; gap:40px; }
        .title-section { grid-column:1/-1; text-align:center; margin-bottom:30px; }
        .title-section h1 { margin:0; font-size:32px; color:#FF5768; }
        .title-section h2 { margin:5px 0 0 0; font-size:18px; color:#333; font-weight:normal; }
        .title-divider { width:60px; height:3px; background:#4DC9A5; border:none; margin:10px auto 0; border-radius:2px; }
        .sensor-grid { display:grid; gap:20px; }
        .sensor-item { display:flex; flex-direction:column; gap:8px; }
        .sensor-item input { height:35px; font-size:16px; padding:10px; border-radius:10px; border:2px solid #E0D8C3; background-color:#f7f4ef; }
        .sensor-item button { height:35px; font-size:16px; cursor:pointer; background-color:#4DC9A5; color:white; border:3px solid #7FE0CC; width:150px; margin:0 auto; border-radius:8px; }
        .col2 { display:grid; grid-template-rows:1fr 1fr; justify-items:center; align-items:center; gap:30px; }
        .circle { width:100px; height:100px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:24px; text-decoration:none; color:white; border:none; cursor:pointer; }
        .circle[data-state="on"] { background:linear-gradient(135deg,#FF6B6B,#FF8787); }
        .circle[data-state="off"] { background:linear-gradient(135deg,#4D9EF6,#6AB0FF); }
        .col1, .col3 { background-color:#fcf3f9; padding:20px; border-radius:15px; }
    </style>

    <script>
        function updateSensors() {
            fetch('/ultrasonic').then(r => r.text()).then(data => document.getElementById('ultrasonic').value = data);
            fetch('/temperature').then(r => r.text()).then(data => document.getElementById('temperature').value = data);
        }

        function sendToLCD(sensor) {
            let value = document.getElementById(sensor).value;
            fetch('/lcd_write?sensor=' + sensor + '&value=' + encodeURIComponent(value))
                .then(r => r.text())
                .then(data => console.log("LCD:", data));
        }

        function toggleLED(state) {
            fetch('/led/' + state)
                .then(r => r.text())
                .then(data => console.log(data));
        }

        setInterval(updateSensors, 2000);
        window.onload = updateSensors;
        
        function sendCustomText() {
            let value = document.getElementById('custom_text').value;
            fetch('/lcd_custom?value=' + encodeURIComponent(value))
                .then(r => r.text())
                .then(data => console.log("LCD:", data));
        }
    </script>
</head>

<body>
<div class="container-wrapper">
<div class="container">

    <div class="title-section">
        <h1>ESP32 Web Server Control</h1>
        <h2>IoT 360 002 - Group 6</h2>
        <hr class="title-divider">
    </div>

    <div class="col1">
        <div class="sensor-grid">
            <div class="sensor-item">
                <label>Ultrasonic</label>
                <input type="text" id="ultrasonic" readonly>
                <button onclick="sendToLCD('ultrasonic')">Show Distance</button>
            </div>
            <div class="sensor-item">
                <label>Temperature</label>
                <input type="text" id="temperature" readonly>
                <button onclick="sendToLCD('temperature')">Show Temp</button>
            </div>
        </div>
    </div>

    <div class="col2">
        <button class="circle" data-state="on" onclick="toggleLED('on')">ON</button>
        <button class="circle" data-state="off" onclick="toggleLED('off')">OFF</button>
    </div>

    <div class="col3">
        <div class="sensor-item">
            <label>Textbox</label>
            <input type="text" id="custom_text">
            <button onclick="sendCustomText()">Send</button>
        </div>
    </div>

</div>
</div>
</body>
</html>
"""

# ---------- Server ----------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
print("Web server running")

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    print("Request:", request)

    # ---------- LED Control ----------
    if "/led/on" in request:
        led.on()
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nLED ON")
        conn.close()
        continue
    elif "/led/off" in request:
        led.off()
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nLED OFF")
        conn.close()
        continue

    # ---------- Temperature ----------
    elif "/temperature" in request:
        temp, hum = read_dht11()
        response = str(temp) if temp is not None else "Error"
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
        conn.sendall(response)
        conn.close()
        continue

    # ---------- Ultrasonic ----------
    elif "/ultrasonic" in request:
        distance = read_ultrasonic()
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
        conn.sendall(str(distance))
        conn.close()
        continue

    # ---------- LCD Write ----------
    elif "/lcd_write" in request:
        try:
            parts = request.split(' ')[1].split('?')[1]
            params = parse_query(parts)
            sensor = params.get('sensor')
            value = url_decode(params.get('value'))

            if sensor == 'ultrasonic':
                lcd.move_to(0, 0)
                lcd.putstr(" " * 16)  # clear line 0
                num_part = value.split()[0] if value else ""
                lcd.move_to(0, 0)
                lcd.putstr(num_part[:16])
                if len(num_part) < 16 and 'cm' in value:
                    lcd.move_to(len(num_part), 0)
                    lcd.putstr("cm")

            elif sensor == 'temperature':
                lcd.move_to(0, 1)
                lcd.putstr(" " * 16)  # clear line 1
                lcd.move_to(0, 1)
                lcd.putstr(value[:16])

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nDone")
        except:
            conn.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nError")
        conn.close()
        continue

    # ---------- LCD Custom Text ----------
    elif "/lcd_custom" in request:
        try:
            parts = request.split(' ')[1].split('?')[1]
            params = parse_query(parts)
            value = url_decode(params.get('value'))

            # Clear both lines
            lcd.move_to(0, 0)
            lcd.putstr(" " * 16)
            lcd.move_to(0, 1)
            lcd.putstr(" " * 16)

            # Display text
            lcd.move_to(0, 0)
            if len(value) <= 16:
                lcd.putstr(value)
            else:
                for i in range(0, len(value)-15):  # start from first character
                    lcd.move_to(0, 0)
                    lcd.putstr(value[i:i+16])
                    time.sleep(0.3)
                lcd.move_to(0, 0)
                lcd.putstr(value[-16:])

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nDone")
        except:
            conn.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nError")
        conn.close()
        continue

    # ---------- Default: Send web page ----------
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    conn.sendall(web_page())
    conn.close()

