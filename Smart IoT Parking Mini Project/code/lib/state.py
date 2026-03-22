class RuntimeState:
    def __init__(self, total_slots):
        self.total_slots = total_slots
        self.occupied_slots = 0
        self.available_slots = total_slots
        self.temperature = 0
        self.humidity = 0
        self.distance_cm = -1

        self.entry_gate_open = False
        self.entry_gate_mode = "idle"
        self.entry_no_detect_since = None
        self.last_auto_trigger_ms = 0

        self.exit_gate_open = False
        self.exit_gate_mode = "idle"
        self.exit_opened_at_ms = None
        self.last_exit_trigger_ms = 0

        self.last_valid_temp = 0
        self.last_valid_hum = 0
        self.last_event = "boot"
        self.last_event_ts = 0

        self.system_led_on = False

        # manual override:
        # None  = auto mode
        # True  = force ON
        # False = force OFF
        self.manual_light_override = None

        # auto light timers
        self.entry_light_until_ms = None
        self.exit_light_until_ms = None

        self.slot1_present = False
        self.slot1_timer_started_ms = None
        self.slot1_elapsed_seconds = 0
        self.last_fee_amount = 0.0
        self.last_fee_seconds = 0
        self.fee_pending = False
        self.last_fee_display_until_ms = 0