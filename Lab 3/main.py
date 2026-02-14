from machine import Pin, PWM
from time import sleep
import tm1637
import BlynkLib

# ========== BLYNK SETUP ==========
BLYNK_AUTH = "YOUR_BLYNK_AUTH_TOKEN"
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# ========== HARDWARE ==========
ir = Pin(27, Pin.IN)
servo = PWM(Pin(13), freq=50)
display = tm1637.TM1637(clk=Pin(22), dio=Pin(21))

# ========== VARIABLES ==========
count = 0
auto_mode = True
last_ir = 0

# ========== SERVO FUNCTION ==========
def set_servo(angle):
    angle = max(0, min(180, angle))
    duty = int(26 + (angle / 180) * (128 - 26))
    servo.duty(duty)

set_servo(0)

# ========== BLYNK WIDGETS ==========
@blynk.on("V0")  # Servo slider (0–180)
def servo_slider(value):
    if not auto_mode:
        set_servo(int(value[0]))

@blynk.on("V1")  # Auto / Manual switch
def mode_switch(value):
    global auto_mode
    auto_mode = bool(int(value[0]))
    blynk.virtual_write(5, "AUTO" if auto_mode else "MANUAL")

# ========== MAIN LOOP ==========
while True:
    blynk.run()

    ir_state = ir.value()

    # IR status display
    blynk.virtual_write(2, "Detected" if ir_state else "Not Detected")

    # Automatic mode logic
    if auto_mode and ir_state == 1 and last_ir == 0:
        count += 1

        # Open gate
        set_servo(90)
        sleep(2)

        # Close gate
        set_servo(0)

        # Update displays
        display.number(count)
        blynk.virtual_write(3, count)

    last_ir = ir_state
    sleep(0.1)
