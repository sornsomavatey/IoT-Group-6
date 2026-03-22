from machine import Pin, PWM, I2C
import time
import dht
import tm1637
from machine_i2c_lcd import I2cLcd
AUTO_LIGHT_HOLD_MS = 5000
from lib.config import (
    SSID, PASSWORD,
    I2C_ADDR, I2C_ROWS, I2C_COLS, TOTAL_SLOTS,
    PIN_I2C_SCL, PIN_I2C_SDA, PIN_TRIG, PIN_ECHO,
    PIN_IR1, PIN_IR2, PIN_IR3, PIN_IR_EXIT,
    PIN_STATUS_LED, PIN_SERVO_ENTRY, PIN_SERVO_EXIT,
    PIN_TM1637_CLK, PIN_TM1637_DIO, PIN_DHT,
    ENTRY_OPEN_DUTY, ENTRY_CLOSE_DUTY,
    EXIT_OPEN_DUTY, EXIT_CLOSE_DUTY,
    CAR_DETECTION_THRESHOLD, AUTO_CLOSE_DELAY_MS, EXIT_CLOSE_DELAY_MS,
    FEE_MODE, FEE_RATE,
)
from lib.wifi_manager import WiFiManager
from lib.ultrasonic import UltrasonicSensor
from lib.state import RuntimeState


class SmartParkingController:
    def __init__(self):
        self.wifi = WiFiManager(SSID, PASSWORD)
        self.wifi.connect()

        self.i2c = I2C(0, scl=Pin(PIN_I2C_SCL), sda=Pin(PIN_I2C_SDA), freq=400000)
        self.lcd = I2cLcd(self.i2c, I2C_ADDR, I2C_ROWS, I2C_COLS)

        self.ultrasonic = UltrasonicSensor(PIN_TRIG, PIN_ECHO)
        self.ir1 = Pin(PIN_IR1, Pin.IN)
        self.ir2 = Pin(PIN_IR2, Pin.IN)
        self.ir3 = Pin(PIN_IR3, Pin.IN)
        self.ir_exit = Pin(PIN_IR_EXIT, Pin.IN)
        self.status_led = Pin(PIN_STATUS_LED, Pin.OUT)
        self.servo_entry = PWM(Pin(PIN_SERVO_ENTRY), freq=50)
        self.servo_exit = PWM(Pin(PIN_SERVO_EXIT), freq=50)
        self.tm = tm1637.TM1637(Pin(PIN_TM1637_CLK), Pin(PIN_TM1637_DIO))
        self.dht_sensor = dht.DHT11(Pin(PIN_DHT))
        self.state = RuntimeState(TOTAL_SLOTS)

        try:
            self.tm.set_brightness(7)
        except Exception:
            pass

        self.servo_close(self.servo_entry, ENTRY_CLOSE_DUTY)
        self.servo_close(self.servo_exit, EXIT_CLOSE_DUTY)
        self.status_led.value(0)
        self.state.manual_light_on = False
        self.refresh_sensors()
        self.update_display()
        self.update_lcd()

    def set_event(self, name):
        self.state.last_event = name
        self.state.last_event_ts = time.ticks_ms()

    def servo_open(self, servo, duty_value):
        servo.duty(duty_value)

    def servo_close(self, servo, duty_value):
        servo.duty(duty_value)

    def refresh_sensors(self):
        self.state.occupied_slots, self.state.available_slots = self.get_slot_count()
        self.state.temperature, self.state.humidity = self.read_temp()
        self.state.distance_cm = self.ultrasonic.read_cm()
        self._update_fee_timer()
        self._update_system_led()

    def get_slot_count(self):
        occupied = 0
        if self.ir1.value() == 0:
            occupied += 1
        if self.ir2.value() == 0:
            occupied += 1
        if self.ir3.value() == 0:
            occupied += 1
        return occupied, TOTAL_SLOTS - occupied

    def read_temp(self):
        try:
            self.dht_sensor.measure()
            temp = self.dht_sensor.temperature()
            hum = self.dht_sensor.humidity()
            if 0 <= temp <= 80 and 0 <= hum <= 100:
                self.state.last_valid_temp = temp
                self.state.last_valid_hum = hum
        except Exception as exc:
            print("DHT error:", exc)
        return self.state.last_valid_temp, self.state.last_valid_hum

    def update_display(self):
        try:
            self.tm.show_number(self.state.available_slots)
        except Exception:
            try:
                self.tm.show_digit(self.state.available_slots)
            except Exception as exc:
                print("TM1637 error:", exc)

    def _show_fee_lcd(self):
        try:
            self.lcd.clear()
            self.lcd.move_to(0, 0)
            self.lcd.putstr("Fee: {:.2f}".format(self.state.last_fee_amount))
            self.lcd.move_to(0, 1)
            self.lcd.putstr("Time:{}s".format(self.state.last_fee_seconds))
        except Exception:
            pass

    def update_lcd(self):
        now = time.ticks_ms()
        if self.state.last_fee_display_until_ms and time.ticks_diff(self.state.last_fee_display_until_ms, now) > 0:
            self._show_fee_lcd()
            return

        try:
            self.lcd.clear()
            self.lcd.move_to(0, 0)
            self.lcd.putstr("S:{} O:{} F:{:.2f}".format(
                self.state.available_slots,
                self.state.occupied_slots,
                self.state.last_fee_amount,
            )[:16])
            self.lcd.move_to(0, 1)
            entry = "OP" if self.state.entry_gate_open else "CL"
            exitg = "OP" if self.state.exit_gate_open else "CL"
            self.lcd.putstr("T:{} E:{} X:{}".format(self.state.temperature, entry, exitg)[:16])
        except Exception:
            pass

    def _update_system_led(self):
        now = time.ticks_ms()

        entry_auto = (
            self.state.entry_light_until_ms is not None and
            time.ticks_diff(self.state.entry_light_until_ms, now) > 0
        )

        exit_auto = (
            self.state.exit_light_until_ms is not None and
            time.ticks_diff(self.state.exit_light_until_ms, now) > 0
        )

        auto_light = entry_auto or exit_auto

        if self.state.manual_light_override is True:
            light_on = True
        elif self.state.manual_light_override is False:
            light_on = False
        else:
            light_on = auto_light

        self.state.system_led_on = bool(light_on)
        self.status_led.value(1 if light_on else 0)

    def turn_light_on(self, source="manual"):
        self.state.manual_light_override = True
        self.set_event("light_on_" + source)
        self._update_system_led()
        print("Indicator LED ON [{}]".format(source))

    def turn_light_off(self, source="manual"):
        self.state.manual_light_override = False
        self.set_event("light_off_" + source)
        self._update_system_led()
        print("Indicator LED OFF [{}]".format(source))

    def set_entry_gate_state(self, is_open, source="manual"):
        if is_open:
            self.servo_open(self.servo_entry, ENTRY_OPEN_DUTY)
            self.state.entry_gate_open = True
            self.state.entry_gate_mode = source
            self.state.entry_no_detect_since = None
            self.set_event("entry_open_" + source)
            print("Entry gate OPEN [{}]".format(source))
        else:
            self.servo_close(self.servo_entry, ENTRY_CLOSE_DUTY)
            self.state.entry_gate_open = False
            self.state.entry_gate_mode = "idle"
            self.state.entry_no_detect_since = None
            self.set_event("entry_close_" + source)
            print("Entry gate CLOSED [{}]".format(source))
        self._update_system_led()

    def set_exit_gate_state(self, is_open, source="manual"):
        if is_open:
            self.servo_open(self.servo_exit, EXIT_OPEN_DUTY)
            self.state.exit_gate_open = True
            self.state.exit_gate_mode = source
            self.state.exit_opened_at_ms = time.ticks_ms()
            self.set_event("exit_open_" + source)
            print("Exit gate OPEN [{}]".format(source))
        else:
            self.servo_close(self.servo_exit, EXIT_CLOSE_DUTY)
            self.state.exit_gate_open = False
            self.state.exit_gate_mode = "idle"
            self.state.exit_opened_at_ms = None
            self.set_event("exit_close_" + source)
            print("Exit gate CLOSED [{}]".format(source))
        self._update_system_led()

    def open_entry_gate(self, source="manual"):
        self.set_entry_gate_state(True, source)

    def close_entry_gate(self, source="manual"):
        self.set_entry_gate_state(False, source)

    def open_exit_gate(self, source="manual"):
        self.set_exit_gate_state(True, source)

    def close_exit_gate(self, source="manual"):
        self.set_exit_gate_state(False, source)

    def _billing_units(self, elapsed_seconds):
        if FEE_MODE == "hour":
            units = elapsed_seconds / 3600.0
        elif FEE_MODE == "minute":
            units = elapsed_seconds / 60.0
        else:
            units = elapsed_seconds
        if units < 0:
            units = 0
        return units

    def _calculate_fee(self, elapsed_seconds):
        return round(self._billing_units(elapsed_seconds) * FEE_RATE, 2)

    def _update_fee_timer(self):
        now = time.ticks_ms()
        slot1_present = self.ir1.value() == 0

        if slot1_present and not self.state.slot1_present:
            self.state.slot1_present = True
            self.state.slot1_timer_started_ms = now
            self.state.slot1_elapsed_seconds = 0
            self.state.fee_pending = False
            self.state.last_fee_amount = 0.0
            self.state.last_fee_seconds = 0
            self.set_event("slot1_vehicle_detected")

        elif slot1_present and self.state.slot1_present and self.state.slot1_timer_started_ms is not None:
            self.state.slot1_elapsed_seconds = max(0, time.ticks_diff(now, self.state.slot1_timer_started_ms) // 1000)

        elif (not slot1_present) and self.state.slot1_present:
            elapsed_seconds = self.state.slot1_elapsed_seconds
            self.state.slot1_present = False
            self.state.slot1_timer_started_ms = None
            self.state.slot1_elapsed_seconds = 0
            self.state.last_fee_seconds = elapsed_seconds
            self.state.last_fee_amount = self._calculate_fee(elapsed_seconds)
            self.state.fee_pending = True
            self.set_event("parking_fee_ready")

    def run_automation(self):
        self._entry_control()
        self._exit_control()
        self._update_system_led()

    def _entry_control(self):
        now = time.ticks_ms()
        distance = self.state.distance_cm
        available_slots = self.state.available_slots
        car_detected = distance != -1 and distance <= CAR_DETECTION_THRESHOLD

        if self.state.entry_gate_mode == "manual" and self.state.entry_gate_open:
            return

        if car_detected and available_slots > 0:
            self.state.entry_light_until_ms = time.ticks_add(now, AUTO_LIGHT_HOLD_MS)
            if (not self.state.entry_gate_open) and time.ticks_diff(now, self.state.last_auto_trigger_ms) > 2000:
                self.open_entry_gate("auto")
                self.state.last_auto_trigger_ms = now
            self.state.entry_no_detect_since = None
            return

        if car_detected and available_slots == 0:
            self.set_event("parking_full")
            return

        if self.state.entry_gate_mode == "auto" and self.state.entry_gate_open:
            if car_detected:
                self.state.entry_no_detect_since = None
            else:
                if self.state.entry_no_detect_since is None:
                    self.state.entry_no_detect_since = now
                elif time.ticks_diff(now, self.state.entry_no_detect_since) >= AUTO_CLOSE_DELAY_MS:
                    self.close_entry_gate("auto")

    def _exit_control(self):
        now = time.ticks_ms()
        exit_hit = self.ir_exit.value() == 0

        if exit_hit:
            self.state.exit_light_until_ms = time.ticks_add(now, AUTO_LIGHT_HOLD_MS)
            if self.state.fee_pending:
                self.state.last_fee_display_until_ms = time.ticks_add(now, 5000)
                self.set_event("parking_fee_due")
            if (self.state.exit_gate_mode != "manual") and (not self.state.exit_gate_open) and time.ticks_diff(now, self.state.last_exit_trigger_ms) > 2000:
                self.set_exit_gate_state(True, "auto")
                self.state.last_exit_trigger_ms = now

        if self.state.exit_gate_mode == "manual" and self.state.exit_gate_open:
            return

        if self.state.exit_gate_open and self.state.exit_gate_mode == "auto" and self.state.exit_opened_at_ms is not None:
            if time.ticks_diff(now, self.state.exit_opened_at_ms) >= EXIT_CLOSE_DELAY_MS:
                self.set_exit_gate_state(False, "auto")

    def get_status(self):
        return {
            "available_slots": self.state.available_slots,
            "occupied_slots": self.state.occupied_slots,
            "temperature": self.state.temperature,
            "humidity": self.state.humidity,
            "distance_cm": self.state.distance_cm,
            "entry_gate": "OPEN" if self.state.entry_gate_open else "CLOSED",
            "exit_gate": "OPEN" if self.state.exit_gate_open else "CLOSED",
            "system_led": "ON" if self.state.system_led_on else "OFF",
            "light_manual": (
                "ON" if self.state.manual_light_override is True
                else "OFF" if self.state.manual_light_override is False
                else "AUTO"
            ),            
            "wifi": self.wifi.label(),
            "wifi_rssi": self.wifi.rssi(),
            "ip": self.wifi.ip(),
            "last_event": self.state.last_event,
            "source": "esp32",
            "fee_mode": FEE_MODE,
            "fee_rate": FEE_RATE,
            "slot1_vehicle_present": self.state.slot1_present,
            "slot1_elapsed_seconds": self.state.slot1_elapsed_seconds,
            "parking_fee": self.state.last_fee_amount,
            "parking_fee_seconds": self.state.last_fee_seconds,
            "parking_fee_pending": self.state.fee_pending,
        }
def clear_manual_light_override(self, source="manual"):
    self.state.manual_light_override = None
    self.set_event("light_auto_" + source)
    self._update_system_led()
    print("Indicator LED AUTO [{}]".format(source))