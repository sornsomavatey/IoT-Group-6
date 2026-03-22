import os
import threading
import time
from flask import Flask, jsonify, send_file

from services.esp32_client import Esp32Client
from services.blynk_client import BlynkClient
from services.telegram_client import TelegramClient
from services.sync_engine import SyncEngine

ESP32_BASE_URL = os.getenv("ESP32_BASE_URL", "http://192.168.0.45")
BLYNK_TOKEN = os.getenv("BLYNK_TOKEN", "56q-xORQx9rKec76e3-UnXFi-zL-8y3-")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8535506703:AAFONc38bFBpwWEGOcN63rEgjKH5KVKeutM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1283351297")
LOCAL_WEB_PORT = int(os.getenv("LOCAL_WEB_PORT", "5000"))
SYNC_INTERVAL_SECONDS = float(os.getenv("SYNC_INTERVAL_SECONDS", "0.5"))
STATUS_PUSH_EVERY = int(os.getenv("STATUS_PUSH_EVERY", "4"))

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PATH = os.path.join(BASE_DIR, "dashboard.html")

esp32 = Esp32Client(ESP32_BASE_URL)
blynk = BlynkClient(BLYNK_TOKEN)
telegram = TelegramClient(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
sync = SyncEngine(esp32, blynk, telegram)


@app.route("/")
def dashboard():
    return send_file(DASHBOARD_PATH)


@app.route("/api/status")
def api_status():
    try:
        return jsonify({"ok": True, "data": sync.refresh_status(push_blynk=True)})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc), "data": sync.get_cached_status()}), 503


@app.route("/api/gate/open")
def api_gate_open():
    return jsonify({"ok": True, "data": sync.command_entry_gate(True, source="web")})


@app.route("/api/gate/close")
def api_gate_close():
    return jsonify({"ok": True, "data": sync.command_entry_gate(False, source="web")})


@app.route("/api/exit/open")
def api_exit_open():
    return jsonify({"ok": True, "data": sync.command_exit_gate(True, source="web")})


@app.route("/api/exit/close")
def api_exit_close():
    return jsonify({"ok": True, "data": sync.command_exit_gate(False, source="web")})


@app.route("/api/light/on")
def api_light_on():
    return jsonify({"ok": True, "data": sync.command_light(True, source="web")})


@app.route("/api/light/off")
def api_light_off():
    return jsonify({"ok": True, "data": sync.command_light(False, source="web")})


def background_loop():
    loop_count = 0
    while True:
        try:
            sync.handle_blynk_commands()
        except Exception as exc:
            print("Blynk commands error:", exc)

        try:
            sync.handle_telegram_updates()
        except Exception as exc:
            print("Telegram error:", exc)

        loop_count += 1
        if loop_count >= STATUS_PUSH_EVERY:
            try:
                sync.refresh_status(push_blynk=True)
            except Exception as exc:
                print("Status refresh error:", exc)
            loop_count = 0

        time.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    print("ESP32 Base URL:", ESP32_BASE_URL)
    print("Local dashboard on http://127.0.0.1:{}".format(LOCAL_WEB_PORT))
    print("Telegram polling {}".format("enabled" if telegram.enabled() else "disabled"))

    try:
        sync.refresh_status(push_blynk=True)
    except Exception as exc:
        print("Initial refresh failed:", exc)

    thread = threading.Thread(target=background_loop, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=LOCAL_WEB_PORT, debug=False)
