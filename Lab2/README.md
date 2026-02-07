# IoT-Group-6 | lab 2

## Wiring
<p align="center">
  <img src="https://github.com/user-attachments/assets/16cb60a0-a921-4d78-beaa-9c58529b82d3" width="400" alt="Wiring">
  <img src="https://github.com/user-attachments/assets/1334f83c-f06b-45b1-bb5f-b02bd53d5716" width="400" alt="Wiring">
</p> <br>

* The system uses an ESP32, a DHT22 sensor, and a relay module.
* The DHT22 VCC pin is connected to the 3.3V pin on the ESP32.
* The DHT22 GND pin is connected to GND on the ESP32.
* The DHT22 DATA pin is connected to a GPIO pin on the ESP32 for reading temperature and humidity.
* The relay IN pin is connected to a GPIO pin on the ESP32 to control the relay.
  
<br>

## Task 1 - LED Control 
* Watch the video [here](Link) 🎥

<br>

## Task 2 - Sensor Read 
<p align="center">
  <img src="https://github.com/user-attachments/assets/342a6672-150c-48a2-896a-eeefd2b0d9ef" width="400" alt="Task2">
  <img src="https://github.com/user-attachments/assets/523da78e-ce91-4c25-bd8f-6644fabe2418" width="400" alt="Task2">
</p> <br>

* Read DHT11 temperature and ultrasonic distance.
* Show values on the web page (refresh every 1-2 seconds).

<br>

## Task 3 - Sensor → LCD 
<p align="center">
  <img src="https://github.com/user-attachments/assets/96f9cae3-cbc3-45d0-b62d-0d332df0fb2d" width="400" alt="Task3">
</p> <br>

* Add two buttons:
  * 
  * 

<br>

## Task 4 - Bot Command
Watch the video [here](https://youtu.be/jUGsw2-0e0o?feature=shared) 🎥

<br>

## Task 5 - Robustness
<p align="center">
  <img src="https://github.com/user-attachments/assets/0805d56f-def9-4ff2-b377-39b009fcb3fd" width="400" alt="Task5">
  <img src="https://github.com/user-attachments/assets/c3ed03bf-ae75-4782-9c73-2799e6ab3a8f" width="400" alt="Task5">
</p> <br>

* The system automatically reconnects to Wi-Fi if the connection is lost.
* Telegram HTTP errors are handled by printing the error status and skipping the current loop cycle.
* Any errors in the DHT22 sensor readings are caught to prevent the program from crashing.

<br>

## Task 6 - Diagram
<p align="center">
  <img src="https://github.com/user-attachments/assets/d9070229-f0d4-40cf-bbe9-f5651a939811" width="400" alt="Task6">
</p> <br>


