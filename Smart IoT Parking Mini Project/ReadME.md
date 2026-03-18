<div align="center">

# Smart IoT Parking Mini Project

## Project Title:  Park At Your Own RISK

Somavatey SORN, Tyty LIMENG, Darichy LIM, Channeath ROS

Instructor: Prof. Theara SENG

Course: ICT 360 002 - Introduction to Internet of Things

</div>


## 1. Introduction

The Smart IoT Parking Management System is an embedded IoT project developed using the ESP32 microcontroller running MicroPython firmware. The system automates the management of a parking facility by detecting incoming vehicles, controlling a gate barrier, monitoring individual parking slot occupancy, regulating lighting, and reporting environmental data in real time.

The system is designed to be accessed and controlled remotely through three IoT platforms: a Telegram Bot for command-based interaction, a locally hosted Web Server Dashboard for browser-based monitoring and control, and the Blynk mobile application for smartphone remote control.

This project demonstrates the integration of hardware sensors, actuators, and cloud-based services into a unified IoT solution. It reflects practical skills in embedded systems programming, real-time logic design, and multi-platform IoT integration.

## 2. Hardware Description

The following hardware components are used in the system. Each component serves a specific role in the detection, actuation, or display pipeline.

| Component | Role / Description |
|-----------|-------------------|
| ESP32 | Main microcontroller running MicroPython. Manages all sensors, actuators, and IoT platform communication via Wi-Fi. |
| Ultrasonic Sensor (HC-SR04) | Mounted at the parking entry to detect incoming vehicles by measuring distance. Triggers gate-opening logic when threshold is crossed. |
| IR Sensors (x3 minimum) | One sensor per parking slot. Each detects whether a slot is occupied or free. Outputs are polled to update the slot counter. |
| Servo Motor | Controls the physical gate barrier. Rotates to a defined angle to open or close the gate based on system or remote commands. |
| DHT11 Sensor | Measures ambient temperature and humidity inside the parking facility. Data is reported via all three IoT platforms. |
| Relay Module | Controls the parking area lighting circuit. Can be triggered automatically or manually via remote commands. |
| TM1637 4-Digit Display | Displays the current count of available parking slots in real time on a physical LED display at the entry. |
| LCD I2C (16x2) | Displays system status messages such as gate state, temperature, and occupancy directly on the hardware unit. |


## GPIO Pin Configuration

- **Ultrasonic Sensor:** TRIG GPIO 5, ECHO GPIO 18
- **IR Sensors:** GPIO 19, GPIO 21, GPIO 22 (one per slot)
- **Servo Motor:** Signal GPIO 23 (PWM-capable pin)
- **DHT11:** Data GPIO 4
- **Relay Module:** IN GPIO 26
- **TM1637:** CLK GPIO 14, DIO GPIO 13
- **LCD I2C:** SDA GPIO 21, SCL GPIO 22 (shared I2C bus)

## 3. System Architecture

### 3.1 Block Diagram Overview

The system is structured in three logical layers:

- **Sensing Layer:** Ultrasonic sensor, IR sensors, DHT11 — all feeding raw data to the ESP32.
- **Control Layer:** ESP32 (MicroPython) — processes sensor data, runs decision logic, drives actuators (servo, relay, displays).
- **Platform Layer:** Telegram Bot, Web Server Dashboard, Blynk App — all communicating with the ESP32 over Wi-Fi.

### 3.2 Communication Architecture

| Platform | Communication Method |
|----------|----------------------|
| Telegram Bot | HTTPS polling via Telegram Bot API. ESP32 sends GET requests to check for commands and POST requests to send notifications. |
| Web Server | ESP32 hosts a lightweight HTTP server on a local IP. A browser connects to view the dashboard and issue control commands. |
| Blynk App | ESP32 connects to Blynk cloud using a device AUTH token. Widgets on the mobile app sync with virtual pins on the ESP32. |

### 3.3 Component Interaction Flow

1. Vehicle arrives at entry. Ultrasonic sensor detects proximity below threshold distance.
2. ESP32 checks slot availability by reading all IR sensor states.
3. If slots available: Servo opens gate, TM1637 updates count, LCD updates status message.
4. If no slots available: Gate remains closed, Telegram notification is sent.
5. After vehicle enters, servo closes gate automatically after a timed delay.
6. IR sensor in the assigned slot transitions to occupied state.
7. Updated status is pushed simultaneously to Web Server, Blynk, and Telegram.

## 4. Software Architecture

### 4.1 File Structure

- **main.py** — Entry point. Initializes all hardware modules and starts the main async loop.
- **config.py** — Stores Wi-Fi credentials, Telegram token, Blynk token, and GPIO pin definitions.
- **sensors.py** — Functions for reading ultrasonic distance, IR states, and DHT11 data.
- **actuators.py** — Functions for controlling servo angle, relay state, TM1637, and LCD output.
- **telegram_bot.py** — Telegram polling loop, command parser, and notification sender.
- **web_server.py** — HTTP server handler; serves the dashboard HTML and processes API requests.
- **blynk_client.py** — Blynk connection manager, virtual pin read/write handlers, and data push functions.

### 4.2 Main Loop Logic

The main.py file runs a non-blocking cooperative loop that executes the following tasks on each iteration:

- Poll Ultrasonic sensor for vehicle detection at the entry point.
- Read all IR sensor states and compute the current available slot count.
- Update TM1637 display and LCD with current slot count and system status.
- Check Telegram for new incoming commands and respond accordingly.
- Handle any pending Web Server HTTP requests from the browser dashboard.
- Push updated slot count and temperature data to Blynk virtual pins.
- Read DHT11 temperature and humidity on a 10-second interval.
- Evaluate relay state based on auto-mode rules or the last manual command received.

### 4.3 Key Design Decisions

- **Non-blocking architecture:** uasyncio (MicroPython async library) enables concurrent handling of sensors, IoT platform polling, and actuator control without any single task blocking others.
- **Debounce logic:** IR sensor readings are debounced with a short hold-time to prevent false slot state transitions due to vibration or electrical noise.
- **Gate state machine:** Gate states are OPEN, CLOSED, OPENING, and CLOSING. This prevents conflicting simultaneous commands from multiple platforms.
- **Automatic Wi-Fi reconnection:** If the Wi-Fi connection drops, the system continues local sensor and actuator operations and reattempts reconnection every 10 seconds.


## 5. IoT Integration

### 5.1 Telegram Bot

The Telegram Bot provides a command-line-style interface for remote control and status queries. The bot is registered via BotFather and authenticates using a unique token stored in config.py. The ESP32 polls the getUpdates API endpoint to receive commands.

| Command | Description |
|---------|-------------|
| /status | Returns full system status: gate state, slot count, temperature, humidity, and relay state. |
| /open | Manually commands the servo to open the gate regardless of occupancy state. |
| /close | Manually commands the servo to close the gate. |
| /slots | Returns the number of available and occupied parking slots. |
| /temp | Returns the current DHT11 temperature (°C) and humidity (%) readings. |
| /light_on | Activates the relay to turn on the parking area lights. |
| /light_off | Deactivates the relay to turn off the parking area lights. |

Automated notifications are sent when: a vehicle is detected at entry, the gate opens or closes, all slots become full, or a slot becomes free after the lot was full.

### 5.2 Web Server Dashboard

The ESP32 hosts an HTTP server accessible from any browser on the same Wi-Fi network. The dashboard is a single-page HTML/CSS/JavaScript interface stored on the ESP32 file system and served on request.

Dashboard displays and controls:

- Live count of available parking slots with color-coded indicator.
- Current temperature and humidity from DHT11.
- Gate status indicator (Open / Closed) with timestamp of last change.
- Relay and lighting status indicator.
- Manual Open Gate and Close Gate action buttons.
- Manual Light ON and Light OFF toggle buttons.

The dashboard uses periodic JavaScript fetch calls (polling every 2 seconds) to retrieve JSON data from the ESP32 and update the UI dynamically without reloading the page.


### 5.3 Blynk App

The Blynk platform enables smartphone-based monitoring and control. The ESP32 connects to the Blynk cloud server using a device authentication token. Widget states are synced via virtual pins.

| Virtual Pin | Widget / Function |
|-------------|-------------------|
| V0 | Button widget — Triggers gate open/close servo command. |
| V1 | Gauge or Label widget — Displays current temperature in degrees Celsius. |
| V2 | Value Display widget — Shows the current count of available parking slots. |
| V3 | Switch widget — Manual relay control for parking area lighting. |

The ESP32 pushes temperature and slot count to Blynk every 5 seconds using Blynk.virtualWrite(). The gate button operates in PUSH mode to trigger a one-time open/close toggle command.

## 6. Working Process Explanation

### 6.1 Automatic Vehicle Entry Flow

**Step 1 Detection:** The ultrasonic sensor continuously measures distance at the parking entry. When a vehicle is detected within the configured threshold (e.g., 20 cm), vehicle detection is triggered.

**Step 2 Slot Check:** The ESP32 reads all IR sensors. If at least one slot is unoccupied, the system proceeds. If all slots are full, the gate does not open and a Telegram notification is sent.

**Step 3 Gate Opens:** The servo rotates to the open angle. The LCD displays 'Gate Open'. A Telegram notification and Blynk/Web Server updates are sent simultaneously.

**Step 4 Vehicle Passes:** After a configurable hold time, the servo closes the gate automatically.

**Step 5 Slot Update:** The relevant IR sensor transitions to occupied. The slot counter decrements by one. TM1637, LCD, Web Dashboard, Blynk, and Telegram all reflect the new count.

### 6.2 Full Parking Scenario

When all IR sensors read occupied, the gate is locked out from automatic opening. Any vehicle detection at the entry results in a Telegram alert ('Parking Full, Gate Locked') and the TM1637 displays 0 available slots. Manual override remains possible via all three platforms.

### 6.3 Manual Override Flow

Operators can override automatic behavior at any time using Telegram commands, the Web Dashboard buttons, or Blynk widgets. A manual command received by any platform updates the


shared system state and the change is reflected across all platforms within the next poll/push cycle (within 2-5 seconds).

### 6.4 Lighting Logic

In Auto mode, the relay activates lights when at least one slot becomes occupied and deactivates them when the lot is fully empty. In Manual mode, the operator explicitly controls the relay via /light_on, /light_off (Telegram), the dashboard buttons (Web), or the relay switch widget (Blynk).

## 7. Challenges Faced

### 7.1 Slow ESP32



### 7.2 Wi-Fi Stability

MicroPython on the ESP32 occasionally dropped its Wi-Fi connection during extended operation. A watchdog-style reconnection mechanism was implemented so that if the connection drops, the ESP32 continues running local sensor and actuator operations while reattempting Wi-Fi reconnection every 10 seconds in the background.

### 7.3 Servo Motor Jitter

The servo motor exhibited small jitter movements when PWM signals were generated alongside intensive processing tasks. This was resolved by increasing PWM frequency precision and adding a brief stabilization delay before releasing the PWM signal after each servo command.

### 7.4 Telegram API Rate Limiting

Polling the Telegram Bot API too frequently triggered 429 Too Many Requests HTTP responses. The polling interval was increased to a 1-second minimum, and an exponential backoff strategy was added for repeated API errors to avoid persistent lockout.

### 7.5 Time Limitation

This project is a big project with a short deadline plus there are more work that we have to do simultaneously 


## 8. Future Improvements

- **License Plate Recognition:** Add an ESP32-CAM module to capture vehicle license plates at entry and process them via a cloud OCR API for automated access logging.

- **Mobile Payment Integration:** Connect a payment gateway so drivers can pay for reserved slots directly through the Blynk app or Web Dashboard.

- **MQTT Protocol Migration:** Replace HTTP-based polling with MQTT (e.g., via HiveMQ or Mosquitto) for significantly faster and more efficient real-time communication.

- **Cloud Database Logging:** Store all entry/exit events, slot occupancy history, and temperature readings in a cloud database such
