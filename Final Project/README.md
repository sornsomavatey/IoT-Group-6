# SnapBooth System Summary

## 1. Overview

SnapBooth is a smart hands free photobooth that allows users to take photos using a simple high five hand gesture instead of pressing a button or using a remote. The system uses an ESP32-CAM for live video, Python with MediaPipe for gesture detection, Flask for backend control, and Telegram for photo collection. Once a high five is detected, SnapBooth starts a countdown, activates the buzzer and ring light, captures the photo, applies the selected frame, and sends the final image to Telegram that creates a smooth and interactive experience for events and social gatherings.

- Main goal: make photo taking automatic, contact free, and easy for all guests.
- Key feature: high five gesture detection as the photo trigger.
- User experience: countdown display, buzzer sounds, ring light effects, and instant delivery.
- Final output: a framed photo sent directly to Telegram.

---

## 2. Problem Statement

Traditional photobooths often require users to press buttons or use a remote control. This can interrupt the experience, especially during events where guests want something fast, simple, and fun.

SnapBooth solves these problems by using gesture detection and automated feedback.

### Main Problems

- Manual triggers like pressing buttons make the experience less convenient.
- Lack of audio feedback makes it unclear whether the countdown has started or whether the photo was captured.
- Photos are often stored locally instead of being delivered instantly.
- ESP32-CAM has limited streaming ability and cannot support many direct video connections at the same time.
- Frame choices from the user interface must be properly sent to the backend before capture.

---

## 3. Solution

SnapBooth solves the problem by making the photobooth automatic and handsfree. Instead of pressing a button or using a timer, users only need to show a high five gesture in front of the camera. The system then starts a countdown, turns on the ring light, plays buzzer sounds, captures the photo, adds the selected frame, and sends it to Telegram.
 
Key Solutions
  * Uses high five gesture detection instead of manual buttons.
  * Shows a 3-2-1 countdown before taking the photo.
  * Uses a buzzer to give sound feedback.
  * Uses a ring light to improve photo lighting.
  * Adds the user’s selected photo frame.
  * Sends the final photo instantly to Telegram.
  * Keeps the system stable by letting only the backend connect directly to the ESP32-CAM.

---

## 4. Hardware

SnapBooth uses several hardware components connected through a local Wi-Fi network.

<p align="center">
  <img src="https://github.com/user-attachments/assets/bc04b635-50c2-4f01-928c-cc36819db643" width="400"  alt="Other">
  <img src="https://github.com/user-attachments/assets/133c0f14-f799-414a-a621-3614a6733484" width="400" alt="Other">
  <img src="https://github.com/user-attachments/assets/21c20513-339c-46f7-81d7-d80d78fa592c" width="400" alt="Other">
  <img src="https://github.com/user-attachments/assets/618385a2-3ebb-4407-8c2e-66372600c0c9" width="400" alt="Other">
</p> <br>

| Hardware | Purpose |
|---|---|
| ESP32-CAM | Captures the live video stream and photo frames |
| ESP32 | control the external hardware components of the SnapBooth system, such as the ring light and buzzer. |
| Ring Light ESP32 | Provides lighting during countdown and flash during capture |
| Buzzer ESP32 | Gives sound feedback for countdown, success, or error |
| Host PC | Runs Flask server, gesture detection, photo processing, and Telegram delivery |
| Wi-Fi Network | Connects the camera, peripherals, server, and web interface |

### Hardware Role Summary

- The ESP32-CAM provides the camera feed.
- The ring light improves photo lighting and gives visual feedback.
- The buzzer gives audio cues so users know what is happening.
- The host machine controls the full system and processes the photo.
- Telegram is used as the final delivery platform.

---

## 5. System Architecture

SnapBooth is organized into different layers so each part has a clear responsibility.

| Layer | Component | Responsibility |
|---|---|---|
| Hardware Layer | `ESP32-CAM` | Provides the camera stream |
| Detection Layer | `gesture.py` | Detects the high-five gesture using MediaPipe |
| Control Layer | `main.py` | Runs the main booth logic and state machine |
| Server Layer | `server.py` | Provides Flask API, status updates, and live stream sharing |
| Frontend Layer | `index.html` | Allows users to choose frames, view camera preview, and see status |
| Peripheral Layer | `ringlight.py` | Controls the ring light and buzzer |
| Delivery Layer | `telegram.py` | Sends the final photo to Telegram |

### Simple System Flow

1. User opens the web interface.
2. User selects a frame style, color, and theme.
3. User enters the capture page.
4. The system activates gesture detection.
5. ESP32-CAM sends video frames to the Python backend.
6. MediaPipe detects a high-five gesture.
7. Countdown starts: 3 → 2 → 1.
8. Ring light turns on and buzzer plays countdown sounds.
9. Photo is captured.
10. Selected frame is applied to the photo.
11. Photo is sent to Telegram.
12. System resets and waits for the user to take the next picture or next user.

---

## 6. Decision Logic

SnapBooth uses a state machine to control the full capture process clearly and reliably.

| State | Description |
|---|---|
| IDLE | System waits for a high-five gesture |
| COUNTDOWN | Countdown begins, ring light turns on, buzzer plays |
| CAPTURE | Camera captures the photo and ring light flashes |
| SENDING | Photo is framed and sent to Telegram |
| RESULT | System shows success or error, then resets |

### Key Design Decisions

- Use a high five gesture because it is simple, contact-free, and easy for users to understand.
- Use only one direct ESP32-CAM stream connection to avoid overloading the camera.
- Let the backend share the camera stream with the web interface.
- Use debounce logic so the system does not trigger from random hand movement.
- Disable gesture detection during countdown to prevent duplicate captures.
- Apply the selected frame only after capture to keep the live preview smooth.
- Allow the system to continue working even if the buzzer or ring light is offline.

---

## 7. Overall Summary

SnapBooth is a smart hands free photobooth that lets users take photos using a simple high five gesture instead of pressing a button or using a remote. The system uses an ESP32-CAM for live video, Python with MediaPipe for gesture detection, Flask for backend control, and Telegram for instant photo delivery. Once a high five is detected, SnapBooth starts a countdown, activates the buzzer and ring light, captures the photo, applies the selected frame, and sends the final image to Telegram, creating a smooth and interactive experience for events and social gatherings.
  
 <!--  
  * Main goal: make photo-taking automatic, contact-free, and easy for all guests.
  * Key problem solved: removes the need for manual triggers, remote controls, or someone managing the booth.
  * User experience: guests get visual and audio feedback through countdown display, buzzer sounds, and ring light effects.
  * Core hardware: ESP32-CAM, ring light, buzzer, host computer/Raspberry Pi, and Wi-Fi connection.
  * Core software: Python, Flask, MediaPipe, OpenCV, Vanilla JavaScript, and Telegram Bot API.
  * System flow: gesture detected → countdown starts → photo captured → frame added → photo sent to Telegram.
  * Main logic: the system follows a simple state machine: Idle → Countdown → Capture → Sending → Result.
  * Design advantage: only the backend connects directly to the ESP32-CAM, which prevents streaming overload and keeps the system stable.
-->
