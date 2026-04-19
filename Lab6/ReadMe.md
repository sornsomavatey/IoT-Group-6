# IoT-Group-6 | lab 6

## Task 1 - Read UID from RFID card
<p align="center">
  <img src="https://github.com/user-attachments/assets/16e8c6d9-d9fb-4c55-82c3-aa3e741d8f68" width="500" alt="Task1">
</p> <br>


* Detect card and retrieve its unique ID (UID)

<br>

## Task 2 - Match UID with student database
<p align="center">
  <img src="https://github.com/user-attachments/assets/eb5723ec-3c3e-4986-9e22-14415773830e" width="500" alt="Task2">
  <img src="https://github.com/user-attachments/assets/16e8c6d9-d9fb-4c55-82c3-aa3e741d8f68" width="500" alt="Task1">

</p> <br>

* Compare UID with predefined data
* If found -> valid student
* If not -> unknown card

<br>

## Task 3 - Generate current datetime
<p align="center">
  <img src="https://github.com/user-attachments/assets/3ce4a0c4-e1b4-4469-a2e8-3d7417f1fb21" width="500" alt="Task3">
</p> <br>

* Format:
YYYY-MM-DD HH:MM:SS

<br>

## Task 4 & 5 - UID Conditions
<p align="center">
  <a href="https://youtu.be/0xaZg-RjPCk">
    <img src="https://img.youtube.com/vi/0xaZg-RjPCk/maxresdefault.jpg" width="500" alt="Demo">
  </a>
  <br><br>
  🎥 <i><a href="https://youtu.be/0xaZg-RjPCk">Click to watch the demo</a></i>
</p> <br>

* If UID is valid:
  * Activate buzzer for 0.3 seconds
  * Save data to SD card (CSV format): UID, Name, StudentID, Major, DateTime
  * Send data to Firesto

* If UID is invalid:
  * Activate buzzer for 3 seconds
  * Display: "Unknown Card"
  * Do not save or send data
