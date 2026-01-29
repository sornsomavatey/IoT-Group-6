# IoT-Group-6 | lab 2

## Wiring
<p align="center">
  <img src="https://github.com/user-attachments/assets/bd867a95-13c5-4913-809b-b04a4559a2a5" width="400" alt="Wiring">
  <img src="https://github.com/user-attachments/assets/46a96186-b17c-482e-90d7-c356c392b5d2" width="400" alt="Wiring">
</p> <br>

* The system uses an ESP32, a DHT22 sensor, and a relay module.
* The DHT22 VCC pin is connected to the 3.3V pin on the ESP32.
* The DHT22 GND pin is connected to GND on the ESP32.
* The DHT22 DATA pin is connected to a GPIO pin on the ESP32 for reading temperature and humidity.
* The relay IN pin is connected to a GPIO pin on the ESP32 to control the relay.
  
<br>

## Task 1 - Sensor Read & Print 
<p align="center">
  <img src="https://github.com/user-attachments/assets/663fce69-d8c0-46b9-a11b-3807f9d3edfb" width="400" alt="Task1">
</p> <br>

* The DHT22 sensor is read every 5 seconds
* Temperature and humidity are printed with 2 decimal precision
* Output is visible on the serial monitor 

<br>

## Task 2 - Telegram Send
<p align="center">
  <img src="https://github.com/user-attachments/assets/342a6672-150c-48a2-896a-eeefd2b0d9ef" width="400" alt="Task2">
  <img src="https://github.com/user-attachments/assets/523da78e-ce91-4c25-bd8f-6644fabe2418" width="400" alt="Task2">
</p> <br>

* A ```send_message()``` function is implemented
* A test message is sent successfully to the Telegram group

<br>

## Task 3 - Bot Command
<p align="center">
  <img src="https://github.com/user-attachments/assets/96f9cae3-cbc3-45d0-b62d-0d332df0fb2d" width="400" alt="Task3">
</p> <br>

* The ``/status`` command replies with the current temperature, humidity, and relay state.
* The ``/on`` command turns the relay ON.
* ``/off`` command turns the relay OFF.

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


