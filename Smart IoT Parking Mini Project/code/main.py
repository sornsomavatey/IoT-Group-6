from lib.config import API_PORT, HTTP_TICK_REPEAT, LCD_UPDATE_INTERVAL_MS, SENSOR_CHECK_INTERVAL_MS
from lib.smart_gate import SmartParkingController
from lib.api_server import ApiServer
import time


def main():
    controller = SmartParkingController()
    api = ApiServer(controller, port=API_PORT)
    api.start()

    print("Starting ESP32 controller loop...")
    last_sensor_check = time.ticks_ms()
    last_lcd_update = time.ticks_ms()

    while True:
        now = time.ticks_ms()

        for _ in range(HTTP_TICK_REPEAT):
            api.handle_once()

        if time.ticks_diff(now, last_sensor_check) >= SENSOR_CHECK_INTERVAL_MS:
            controller.refresh_sensors()
            controller.run_automation()
            controller.update_display()
            last_sensor_check = now

        if time.ticks_diff(now, last_lcd_update) >= LCD_UPDATE_INTERVAL_MS:
            controller.update_lcd()
            last_lcd_update = now

        time.sleep_ms(20)


if __name__ == "__main__":
    main()
