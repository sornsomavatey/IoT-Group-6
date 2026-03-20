<div align="center">

# Smart IoT Parking Mini Project

## Project Title:  Park At Your Own RISK

Somavatey SORN, Tyty LIMENG, Darichy LIM, Channeath ROS

Instructor: Prof. Theara SENG

ICT 360 002 - Introduction to Internet of Things

</div>

---

## 1. Project Overview

The Smart IoT Parking System is an embedded IoT solution designed to automate parking management using an ESP32 microcontroller with MicroPython.

The system integrates multiple sensors, actuators, and cloud platforms to provide real-time monitoring, automated gate control, and parking fee calculation.

The system supports three remote control platforms:
* Telegram Bot
* Web Dashboard
* Blynk Mobile Application

All platforms remain synchronized so that any command or status update from one interface is reflected across the entire system.

---

## 2. System Architecture

### Hardware Controller

#### ESP32

**Responsible for:**

* Reading sensors
* Running automation logic
* Controlling gate servos
* Calculating parking fee
* Updating displays
* Providing API endpoints for remote platforms

### Sensors

#### Ultrasonic Sensor

Detects vehicles approaching the **entry gate**.

#### IR Sensors (Parking Slots)

Detects whether parking slots are occupied.

#### IR Exit Sensor (IR4 – Pin 26)

Detects vehicles leaving the parking area.

#### DHT11

Measures environmental conditions:

- Temperature
- Humidity


### Actuators

#### Servo Motors

- Entry gate barrier
- Exit gate barrier

#### LED Indicator (Pin 19)

Replaces the relay module.

Used to show system state such as:

- Gate open
- Manual light control
- System active state

### Displays

#### TM1637 Display

Displays **available parking slots**.

#### I2C LCD Display

Displays system information:

- Slot count
- Temperature
- System status
- Parking fee when exiting

---

## 3. IoT Platforms

The system integrates three IoT interfaces.

### Telegram Bot

Allows users to control and monitor the parking system through commands.

### Web Dashboard

Provides a browser-based control panel for monitoring and manual gate control.

### Blynk Mobile App

Provides mobile monitoring and remote control.

---

## 4. Blynk Virtual Pin Mapping

| VPin | Function |
|------|----------|
| V0 | Available Parking Slots |
| V1 | Temperature |
| V2 | Humidity |
| V3 | Entry Gate Control |
| V4 | Light Control |
| V5 | Exit Gate Control |
| V6 | Parking Fee Status |

---

## 5. Telegram Commands

The system supports the following commands:

| Command | Function |
|---------|----------|
| /status | Show system status |
| /open | Open entry gate |
| /close | Close entry gate |
| /open_exit | Open exit gate |
| /close_exit | Close exit gate |
| /slots | Show available parking slots |
| /temp | Show temperature and humidity |
| /light_on | Turn light ON |
| /light_off | Turn light OFF |
| /fee | Show parking fee |
| /help | Show command list |

---

## 6. Web Dashboard Features

The web interface includes separate control sections.

### Entry Gate Section

- Open Entry Gate
- Close Entry Gate
- Entry gate status display


### Exit Gate Section

- Open Exit Gate
- Close Exit Gate
- Exit gate status display

### Parking Information

Displays:

- Available slots
- Temperature
- Humidity
- Parking fee

### Light Control

- Light ON button
- Light OFF button

---

## 7. Smart Gate System Logic

The Smart Gate system automatically manages vehicle entry and exit using sensors.

### 7.1 Entry Gate Logic

#### Vehicle Detection

When the **Ultrasonic sensor detects a vehicle** within the detection threshold:

1. The system checks available parking slots.
2. If slots are available:
   - Entry gate opens.
3. If parking is full:
   - Gate remains closed.
   - LCD displays **Parking Full**.

#### Automatic Gate Operation
```
Vehicle detected → Check slots
      |
      | Slots available
      V
Open entry gate
      |
Vehicle passes
      |
Close entry gate

```

---

### 7.2 Exit Gate Logic

When **IR Exit Sensor (Pin 26)** detects a vehicle leaving:

1. Exit gate opens automatically.
2. Parking fee is calculated.
3. LCD displays the fee amount.
4. The system sends notifications to:
   - Telegram
   - Web Dashboard
   - Blynk

After the vehicle passes:

- Exit gate closes automatically.

---

### 7.3 Manual Gate Control

Both entry and exit gates support manual operation through:

- Telegram
- Web Dashboard
- Blynk

Manual gates remain open **until a close command is received**.

This prevents accidental gate closure during manual operations.

## 8. Parking Fee Calculation

The system includes a **time-based parking fee feature**.

### Parking Timer Logic

When **Slot 1 IR sensor detects a vehicle:**

- The system starts a timer.

When the vehicle leaves the slot:

- The timer stops.
- Parking duration is calculated.

---

### Fee Calculation

The fee can be configured based on:

- Per second
- Per minute
- Per hour

**Example:**
```
Fee = parking_time × rate
```

--- 

### Fee Display

When the vehicle exits:

The system displays the fee on:

- LCD Display
- Web Dashboard
- Telegram Bot
- Blynk App

---

## 9. Light Control System

The relay module has been replaced with an **LED indicator on Pin 19**.

The LED can be controlled through:

- Web dashboard
- Telegram commands
- Blynk mobile app

**Functions:**

- Manual ON
- Manual OFF

---

## 10. Cross-Platform Synchronization

All platforms are synchronized through the system logic.

### Example: If gate opened from Telegram

```
Telegram command
        ↓
ESP32 executes gate open
        ↓
Status updated
        ↓
Web dashboard updated
        ↓
Blynk updated
```

This ensures all platforms always show the same system state.

---

## 11. Smart Features Implemented

The system includes several intelligent features:

- Automatic gate control
- Slot availability detection
- Smart parking fee calculation
- Multi-platform remote control
- Real-time monitoring
- Automatic exit gate operation
- Cross-platform synchronization
- Parking status display
- Environmental monitoring

---

## 12. System Workflow Summary

```
Vehicle arrives
      ↓
Ultrasonic detects car
      ↓
Check available slots
      ↓
Gate opens if slot available
      ↓
Car parks in slot
      ↓
Slot sensor starts parking timer
      ↓
Vehicle exits
      ↓
Exit sensor triggered
      ↓
Parking fee calculated
      ↓
Gate opens
      ↓
Fee displayed on LCD + IoT platforms
```

---

## 13. Future Improvements

Possible enhancements include:

- License plate recognition
- Automatic billing payment system
- Mobile parking reservation
- AI-based slot prediction
- Cloud database logging

---
<br>
<p align="center">
  <img src="https://github.com/user-attachments/assets/7cd90d12-451c-42f2-94af-5693f24237cc" width="500" alt="Task3">
</p> <br>

