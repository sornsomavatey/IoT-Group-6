# LAB 6 – Smart RFID System with Cloud & SD Logging

## Overview
An ESP32-based attendance system that reads RFID cards, identifies students,
logs records to an SD card (CSV) and Firestore, and gives audio feedback via a buzzer.

---

## Files Included

| File | Description |
|------|-------------|
| `main.py` | Main application logic |
| `mfrc522.py` | MFRC522 RFID driver |
| `sdcard.py` | SPI SD card driver |
| `attendance.csv` | Sample CSV output |
| `README.md` | This document |

---

## Hardware

| Component | ESP32 Pin |
|-----------|-----------|
| RFID SDA (SS) | GPIO 5 |
| RFID SCK | GPIO 18 |
| RFID MOSI | GPIO 23 |
| RFID MISO | GPIO 19 |
| RFID RST | GPIO 4 |
| SD CS | GPIO 15 |
| SD SCK | GPIO 14 |
| SD MOSI | GPIO 13 |
| SD MISO | GPIO 12 |
| Buzzer (+) | GPIO 2 |
| Buzzer (–) | GND |

---

## Setup Instructions

### 1. Install MicroPython on ESP32
1. Download the latest ESP32 MicroPython firmware from https://micropython.org/download/ESP32_GENERIC/
2. Flash with: `esptool.py --chip esp32 erase_flash` then `esptool.py write_flash 0x1000 firmware.bin`

### 2. Configure `main.py`
Edit the following constants at the top of `main.py`:

```python
WIFI_SSID        = "YOUR_WIFI_SSID"
WIFI_PASSWORD    = "YOUR_WIFI_PASSWORD"
FIREBASE_PROJECT = "YOUR_PROJECT_ID"
```

### 3. Find Your Card UIDs
Upload `main.py` temporarily without the student DB and run it in Thonny.
Scan your cards — the UID will print to the console. Copy those UIDs into `STUDENT_DB`.

### 4. Set Up Firestore
1. Go to https://console.firebase.google.com → Create a project
2. Enable Firestore Database (test mode for development)
3. Copy your Project ID into `FIREBASE_PROJECT`
4. The collection name used is `attendance`

### 5. Upload Files to ESP32 (via Thonny)
Upload all three `.py` files to the root of the ESP32:
- `main.py`
- `mfrc522.py`
- `sdcard.py`

### 6. Run
Press the **Run** button in Thonny, or press the ESP32 reset button.
The REPL will show: `[System] Ready. Please scan a card ...`

---

## System Behaviour

| Condition | Buzzer | SD Card | Firestore |
|-----------|--------|---------|-----------|
| Valid card | 0.3 s beep | Saved ✅ | Sent ✅ |
| Unknown card | 3 s beep | Not saved ❌ | Not sent ❌ |

---

## CSV Format
```
UID,Name,StudentID,Major,DateTime
A1:B2:C3:D4,Alice Johnson,6501234001,Computer Engineering,2025-04-10 08:05:33
```

---

## Firestore Document Structure
Each attendance record is stored as a document in the `attendance` collection:
```json
{
  "uid":        "A1:B2:C3:D4",
  "name":       "Alice Johnson",
  "student_id": "6501234001",
  "major":      "Computer Engineering",
  "datetime":   "2025-04-10 08:05:33"
}
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No SD card` error | Check SPI pins and CS pin; ensure card is FAT32 formatted |
| RFID not detected | Verify SPI1 pins; check 3.3 V supply to RC522 |
| Firestore 403 error | Set Firestore rules to `allow read, write: if true;` (test mode) |
| NTP sync fails | Check Wi-Fi credentials; ensure port 123 UDP is open |
| Duplicate scans | Adjust `debounce_time` constant in `main.py` |
