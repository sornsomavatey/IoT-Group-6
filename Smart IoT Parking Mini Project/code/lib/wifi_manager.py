import network
import time


class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.wlan.connect(self.ssid, self.password)
            print("Connecting to Wi-Fi...", end="")
            while not self.wlan.isconnected():
                print(".", end="")
                time.sleep(0.5)
            print("\nConnected! IP:", self.wlan.ifconfig()[0])
        return self.wlan

    def label(self):
        return "CONNECTED" if self.wlan.isconnected() else "DISCONNECTED"

    def rssi(self):
        try:
            return self.wlan.status('rssi')
        except Exception:
            return 0

    def ip(self):
        try:
            return self.wlan.ifconfig()[0] if self.wlan.isconnected() else "0.0.0.0"
        except Exception:
            return "0.0.0.0"
