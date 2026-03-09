# IoT-Group-6 | lab 4

## Wiring
<p align="center">
  <img src="" width="250" alt="Wiring">
  <img src="" width="250" alt="Wiring">
  <img src="" width="250" alt="Wiring">
  <img src="" width="250" alt="Wiring">
  <img src="" width="250" alt="Wiring">
  <img src="" width="250" alt="Wiring">
<br>

## Task 1 - Gas Filtering (Moving Average)
<p align="center">
  <img src="https://github.com/user-attachments/assets/6c4a02c8-5739-4a5f-aef2-1093d569db17" width="500" alt="Task1">
</p> <br>

* Read MQ-5 using ESP32 ADC (12-bit).
* Store the last 5 readings.
* Compute moving average.
* Print raw and averaged value.
* Send averaged value to Node-RED.

<br>

## Task 2 - Gas Risk Classification
<p align="center">
  <img src="https://github.com/user-attachments/assets/966484e0-92f2-4da3-99fa-4bec518caca6" width="500" alt="Task2">
</p> <br>

* Send risk_level with data packet based on defined rules.

<br>

## Task 3 - Fever Detection Logic
<p align="center">
  <img src="https://github.com/user-attachments/assets/ed9586b1-be08-44f1-bfa8-f9d473005d7e" width="500" alt="Task3">
</p> <br>

* Send fever_flag to Node-RED.

<br>

## Task 4 - Pressure & Altitude Monitoring (Grafana)
<p align="center">
  <img src="https://github.com/user-attachments/assets/98bf4285-d6c7-403d-b2cc-428759af53d9" width="500" alt="Task4">
</p> <br>

* Create Grafana panels for:
* Gas Average (Time Series)
* Risk Level Display
* Body Temperature Gauge
* Pressure Graph
* Altitude Graph
* pressure (hPa) from BMP280.
* altitude (meters).
* DS3231 timestamp


<br>

## Task 2 - Servo motor control via  Blynk
* Add a Blynk Slider widget to control servo position.
* Slider position from 0 to 180 degree and the servo is moving following the slider

<p align="center">
  <a href="https://youtu.be/0c2dXrqC7Gs">
    <img src="https://img.youtube.com/vi/0c2dXrqC7Gs/maxresdefault.jpg" width="500" alt="Task2">
  </a>
  <br>
  <br>
  🎥 <i><a href="https://youtu.be/0c2dXrqC7Gs">Click to watch the demo</a></i>
</p>
<br>
