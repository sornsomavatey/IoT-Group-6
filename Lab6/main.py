import time
import uos
from mfrc522 import MFRC522
from machine import Pin, SPI
import urequests
import network
import json
import ntptime

WIFI_SSID     = "Maggie"
WIFI_PASSWORD = "88889999"

FIREBASE_PROJECT = "fir-project-cd6b0"
FIRESTORE_BASE = (
    "https://firestore.googleapis.com/v1/projects/"
    + FIREBASE_PROJECT
    + "/databases/(default)/documents/attendance"
)

STUDENT_DB = {
    "094016140180118": {
        "name": "Somavatey Sorn",
        "student_id": "2024026",
        "major": "Digital Infrastructure",
    },
    "039105218060168": {
        "name": "Darichhy Lim",
        "student_id": "2024083",
        "major": "Software Development",
    },
    "101128188002091": {
        "name": "Channeath Ros",
        "student_id": "2023316",
        "major": "Information Technology",
    },
    "006081003007083": {
        "name": "Tyty Limeng",
        "student_id": "2024480",
        "major": "Cyber Security",
    },
}

BUZZER_PIN    = 4
RFID_CS_PIN   = 22
RFID_RST_PIN  = 16
RFID_SCK_PIN  = 18
RFID_MOSI_PIN = 23
RFID_MISO_PIN = 19
SD_CS_PIN     = 13
SD_SCK_PIN    = 14
SD_MOSI_PIN   = 15
SD_MISO_PIN   = 2


CSV_FILENAME = "attendance.csv"
CSV_HEADER   = "UID,Name,StudentID,Major,DateTime\n"


buzzer = Pin(BUZZER_PIN, Pin.OUT, value=0)

rfid_spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
               sck=Pin(RFID_SCK_PIN),
               mosi=Pin(RFID_MOSI_PIN),
               miso=Pin(RFID_MISO_PIN))
rfid_cs  = Pin(RFID_CS_PIN,  Pin.OUT, value=1)
rfid_rst = Pin(RFID_RST_PIN, Pin.OUT, value=1)
rdr = MFRC522(spi=rfid_spi, gpioCs=rfid_cs, gpioRst=rfid_rst)

sd_cs  = Pin(SD_CS_PIN, Pin.OUT, value=1)
sd_spi = SPI(2, baudrate=400_000, polarity=0, phase=0,
             sck=Pin(SD_SCK_PIN),
             mosi=Pin(SD_MOSI_PIN),
             miso=Pin(SD_MISO_PIN))


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    print("[WiFi] Resetting interface...")
    try:
        wlan.disconnect()
    except:
        pass
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)
    print("[WiFi] Connecting to '" + WIFI_SSID + "' ...")
    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as e:
        print("[WiFi] Connect error:", e)
        return False
    for _ in range(20):
        if wlan.isconnected():
            print("[WiFi] Connected:", wlan.ifconfig())
            try:
                ntptime.settime()
                print("[NTP]  Time synced.")
            except Exception as e:
                print("[NTP]  Sync failed:", e)
            return True
        time.sleep(1)
    print("[WiFi] FAILED - offline mode.")
    return False


def get_datetime_str():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5])


def uid_to_str(uid_bytes):
    return "".join("{:03d}".format(b) for b in uid_bytes)


def beep(duration_sec):
    buzzer.value(1)
    time.sleep(duration_sec)
    buzzer.value(0)


def _sd_mount():
    """Full SD reinitialisation + mount. Safe to call repeatedly."""
    import sdcard
    try:
        uos.umount("/sd")
    except Exception:
        pass
    sd_cs.value(1)
    for _ in range(16):
        sd_spi.write(b"\xFF")
    time.sleep_ms(50)
    try:
        sd  = sdcard.SDCard(sd_spi, sd_cs)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        return True
    except Exception as e:
        print("[SD]   Mount error:", e)
        return False


def _sd_umount():
    """Unmount and commit all cached writes to the physical card."""
    try:
        uos.umount("/sd")
        return True
    except Exception as e:
        print("[SD]   Umount error:", e)
        return False


def mount_sd():
    """
    Startup check: mount, ensure CSV exists with header, then unmount.
    Returns True if the card is usable.
    """
    print("[SD]   Mounting...")
    if not _sd_mount():
        print("[SD]   Failed. Check wiring and FAT32 format.")
        return False
    print("[SD]   Mounted at /sd")

    csv_path = "/sd/" + CSV_FILENAME
    try:
        uos.stat(csv_path)
        print("[SD]   Existing CSV found.")
    except OSError:
        r
        try:
            with open(csv_path, "w") as f:
                f.write(CSV_HEADER)
            print("[SD]   New CSV created with header.")
        except Exception as e:
            print("[SD]   Could not create CSV:", e)
            _sd_umount()
            return False

    _sd_umount()
    print("[SD]   SD card ready.")
    return True


def save_to_sd(uid, name, sid, major, dt):
    """
    Full cycle: mount → append one row → umount.
    umount is what physically commits the data to the card.
    """
    print("[SD]   Mounting for write...")
    if not _sd_mount():
        print("[SD]   Remount failed - record not saved.")
        return

    csv_path = "/sd/" + CSV_FILENAME
    line = "{},{},{},{},{}\n".format(uid, name, sid, major, dt)

    
    try:
        info = uos.stat(csv_path)
        print("[SD]   File size before write:", info[6], "bytes")
    except OSError:
        print("[SD]   WARNING: CSV not found after mount, recreating...")
        try:
            with open(csv_path, "w") as f:
                f.write(CSV_HEADER)
        except Exception as e:
            print("[SD]   Recreate failed:", e)
            _sd_umount()
            return

    
    try:
        with open(csv_path, "a") as f:
            f.write(line)
        info = uos.stat(csv_path)
        print("[SD]   File size after write: ", info[6], "bytes")
        print("[SD]   Row written:", line.strip())
    except Exception as e:
        print("[SD]   Write error:", e)
        _sd_umount()
        return

    
    if _sd_umount():
        print("[SD]   Committed to card: OK")
    else:
        print("[SD]   Commit may have failed!")


def send_to_firestore(uid, name, sid, major, dt):
    payload = {
        "fields": {
            "uid":        {"stringValue": uid},
            "name":       {"stringValue": name},
            "student_id": {"stringValue": sid},
            "major":      {"stringValue": major},
            "datetime":   {"stringValue": dt},
        }
    }
    try:
        resp = urequests.post(
            FIRESTORE_BASE,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if resp.status_code in (200, 201):
            print("[FS]   Firestore OK -", resp.status_code)
        else:
            print("[FS]   Error", resp.status_code)
        resp.close()
    except Exception as e:
        print("[FS]   Failed:", e)


def main():
    print("=" * 45)
    print("  Smart RFID Attendance System - LAB 6")
    print("=" * 45)

    connect_wifi()
    sd_ready = mount_sd()

    print("\n[System] Ready. Scan a card ...\n")

    last_uid   = ("", 0)
    DEBOUNCE_S = 3

    while True:
        try:
            stat, _ = rdr.request(rdr.REQIDL)
        except Exception as e:
            print("[RFID] request error:", e)
            time.sleep(0.5)
            continue

        if stat == rdr.OK:
            try:
                stat, uid_bytes = rdr.anticoll()
            except Exception as e:
                print("[RFID] anticoll error:", e)
                time.sleep(0.5)
                continue

            if stat == rdr.OK and uid_bytes:
                uid_str = uid_to_str(uid_bytes)
                now     = time.time()

                if uid_str == last_uid[0] and (now - last_uid[1]) < DEBOUNCE_S:
                    time.sleep(0.2)
                    continue

                last_uid = (uid_str, now)
                dt = get_datetime_str()
                print("\n[RFID] UID:", uid_str, " at", dt)

                student = STUDENT_DB.get(uid_str)

                if student:
                    name  = student["name"]
                    sid   = student["student_id"]
                    major = student["major"]
                    print("[AUTH] VALID ->", name, "(", sid, ")")
                    beep(0.3)
                    if sd_ready:
                        save_to_sd(uid_str, name, sid, major, dt)
                    send_to_firestore(uid_str, name, sid, major, dt)
                else:
                    print("[AUTH] INVALID -> Unknown Card")
                    beep(3)

        time.sleep(0.2)


if __name__ == "__main__":
    main()
