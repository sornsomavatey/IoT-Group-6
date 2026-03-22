import threading
import time


class SyncEngine:
    BLYNK_SUPPRESS_SECONDS = 4.0
    BLYNK_MATCH_STREAK_REQUIRED = 2

    def __init__(self, esp32, blynk, telegram):
        self.esp32 = esp32
        self.blynk = blynk
        self.telegram = telegram
        self._lock = threading.Lock()
        self._status = {
            'available_slots': 0,
            'occupied_slots': 0,
            'temperature': 0,
            'humidity': 0,
            'distance_cm': -1,
            'entry_gate': 'UNKNOWN',
            'exit_gate': 'UNKNOWN',
            'system_led': 'UNKNOWN',
            'light_manual': 'UNKNOWN',
            'wifi': 'UNKNOWN',
            'wifi_rssi': 0,
            'ip': '0.0.0.0',
            'last_event': 'boot',
            'parking_fee': 0.0,
            'parking_fee_seconds': 0,
            'parking_fee_pending': False,
            'fee_mode': 'minute',
            'fee_rate': 0.50,
            'source': 'local-cache',
        }
        self._expected = {
            self.blynk.VPIN_ENTRY_CONTROL: 0,
            self.blynk.VPIN_SYSTEM_LED: 0,
            self.blynk.VPIN_EXIT_CONTROL: 0,
        }
        self._suppress_until = {
            self.blynk.VPIN_ENTRY_CONTROL: 0.0,
            self.blynk.VPIN_SYSTEM_LED: 0.0,
            self.blynk.VPIN_EXIT_CONTROL: 0.0,
        }
        self._match_streak = {
            self.blynk.VPIN_ENTRY_CONTROL: 0,
            self.blynk.VPIN_SYSTEM_LED: 0,
            self.blynk.VPIN_EXIT_CONTROL: 0,
        }
        self.last_fee_signature = None

    def update_cache(self, status):
        with self._lock:
            self._status.update(status)
            return dict(self._status)

    def get_cached_status(self):
        with self._lock:
            return dict(self._status)

    def _status_to_outputs(self, status):
        return {
            self.blynk.VPIN_AVAILABLE: int(status.get('available_slots', 0) or 0),
            self.blynk.VPIN_TEMP: status.get('temperature', 0) or 0,
            self.blynk.VPIN_HUM: status.get('humidity', 0) or 0,
            self.blynk.VPIN_ENTRY_CONTROL: 1 if status.get('entry_gate') == 'OPEN' else 0,
            self.blynk.VPIN_SYSTEM_LED: 1 if status.get('light_manual') == 'ON' else 0,
            self.blynk.VPIN_EXIT_CONTROL: 1 if status.get('exit_gate') == 'OPEN' else 0,
            self.blynk.VPIN_FEE_STATUS: float(status.get('parking_fee', 0) or 0),
        }

    def sync_status_to_blynk(self, status, source='status'):
        values = self._status_to_outputs(status)
        self.blynk.update_many(values)

        now = time.time()
        for pin in (self.blynk.VPIN_ENTRY_CONTROL, self.blynk.VPIN_SYSTEM_LED, self.blynk.VPIN_EXIT_CONTROL):
            expected = int(values[pin])
            self._expected[pin] = expected
            if source != 'blynk':
                self._suppress_until[pin] = now + self.BLYNK_SUPPRESS_SECONDS
                self._match_streak[pin] = 0
            else:
                self._suppress_until[pin] = 0.0
                self._match_streak[pin] = self.BLYNK_MATCH_STREAK_REQUIRED

    def maybe_notify_fee(self, status):
        pending = bool(status.get('parking_fee_pending'))
        fee = float(status.get('parking_fee', 0) or 0)
        sec = int(status.get('parking_fee_seconds', 0) or 0)
        signature = (pending, fee, sec)
        if not pending or signature == self.last_fee_signature:
            return
        self.last_fee_signature = signature
        mode = status.get('fee_mode', 'minute')
        rate = status.get('fee_rate', 0)
        self.telegram.send(
            'Parking fee ready\n'
            'Fee: {:.2f}\n'
            'Time: {} sec\n'
            'Mode: {}\n'
            'Rate: {}'.format(fee, sec, mode, rate)
        )

    def refresh_status(self, push_blynk=True):
        status = self.esp32.status()
        cached = self.update_cache(status)
        if push_blynk:
            self.sync_status_to_blynk(cached, source='status')
        self.maybe_notify_fee(cached)
        return cached

    def _execute_and_sync(self, action, source='api'):
        status = action()
        cached = self.update_cache(status)
        self.sync_status_to_blynk(cached, source=source)
        self.maybe_notify_fee(cached)
        return cached

    def command_entry_gate(self, open_gate, source='api'):
        return self._execute_and_sync(
            self.esp32.gate_open if open_gate else self.esp32.gate_close,
            source=source,
        )

    def command_light(self, turn_on, source='api'):
        return self._execute_and_sync(
            self.esp32.light_on if turn_on else self.esp32.light_off,
            source=source,
        )

    def command_exit_gate(self, open_gate, source='api'):
        return self._execute_and_sync(
            self.esp32.exit_open if open_gate else self.esp32.exit_close,
            source=source,
        )

    def _handle_blynk_pin(self, pin, callback):
        value = self.blynk.read_int(pin)
        if value is None:
            return
        value = 1 if int(value) else 0
        expected = self._expected[pin]
        now = time.time()

        if now < self._suppress_until[pin]:
            if value == expected:
                self._match_streak[pin] += 1
                if self._match_streak[pin] >= self.BLYNK_MATCH_STREAK_REQUIRED:
                    self._suppress_until[pin] = 0.0
            else:
                self._match_streak[pin] = 0
            return

        if value == expected:
            self._match_streak[pin] = self.BLYNK_MATCH_STREAK_REQUIRED
            return

        callback(value == 1, source='blynk')

    def handle_blynk_commands(self):
        self._handle_blynk_pin(self.blynk.VPIN_ENTRY_CONTROL, self.command_entry_gate)
        self._handle_blynk_pin(self.blynk.VPIN_SYSTEM_LED, self.command_light)
        self._handle_blynk_pin(self.blynk.VPIN_EXIT_CONTROL, self.command_exit_gate)

    def handle_telegram_updates(self):
        for update in self.telegram.get_updates():
            text = ((update.get('message') or {}).get('text') or '').strip().lower()
            if not text:
                continue
            self._dispatch_telegram(text)

    def _dispatch_telegram(self, command):
        try:
            if command == '/status':
                status = self.refresh_status(push_blynk=True)
                self.telegram.send(
                    'System running\n'
                    'Slots: {}\n'
                    'Occupied: {}\n'
                    'Temp: {} C\n'
                    'Humidity: {} %\n'
                    'Entry Gate: {}\n'
                    'Exit Gate: {}\n'
                    'Light: {}\n'
                    'Fee: {:.2f}'.format(
                        status['available_slots'],
                        status['occupied_slots'],
                        status['temperature'],
                        status['humidity'],
                        status['entry_gate'],
                        status['exit_gate'],
                        status['light_manual'],
                        status['parking_fee'],
                    )
                )
            elif command == '/open':
                self.command_entry_gate(True, source='telegram')
                self.telegram.send('Entry gate opened')
            elif command == '/close':
                self.command_entry_gate(False, source='telegram')
                self.telegram.send('Entry gate closed')
            elif command == '/open_exit':
                self.command_exit_gate(True, source='telegram')
                self.telegram.send('Exit gate opened')
            elif command == '/close_exit':
                self.command_exit_gate(False, source='telegram')
                self.telegram.send('Exit gate closed')
            elif command == '/light_on':
                self.command_light(True, source='telegram')
                self.telegram.send('Light indicator turned on')
            elif command == '/light_off':
                self.command_light(False, source='telegram')
                self.telegram.send('Light indicator turned off')
            elif command == '/slots':
                self.telegram.send('Available slots: {}'.format(self.refresh_status(push_blynk=True)['available_slots']))
            elif command == '/temp':
                status = self.refresh_status(push_blynk=True)
                self.telegram.send('Temperature: {} C\nHumidity: {} %'.format(status['temperature'], status['humidity']))
            elif command == '/fee':
                status = self.refresh_status(push_blynk=True)
                self.telegram.send('Parking fee: {:.2f}\nTime: {} sec'.format(status['parking_fee'], status['parking_fee_seconds']))
            elif command == '/help':
                self.telegram.send('/status\n/open\n/close\n/open_exit\n/close_exit\n/light_on\n/light_off\n/slots\n/temp\n/fee')
        except Exception as exc:
            self.telegram.send('Command failed: {}\n{}'.format(command, exc))
