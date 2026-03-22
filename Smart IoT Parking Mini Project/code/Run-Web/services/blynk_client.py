import requests


class BlynkClient:
    BASE_URL = 'https://blynk.cloud/external/api'

    VPIN_AVAILABLE = 'V0'
    VPIN_TEMP = 'V1'
    VPIN_HUM = 'V2'
    VPIN_ENTRY_CONTROL = 'V3'
    VPIN_SYSTEM_LED = 'V4'
    VPIN_EXIT_CONTROL = 'V5'
    VPIN_FEE_STATUS = 'V6'

    def __init__(self, token, timeout=3):
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()

    def enabled(self):
        return bool(self.token)

    def update_many(self, values):
        if not self.enabled():
            return False
        params = {'token': self.token}
        params.update(values)
        response = self.session.get(self.BASE_URL + '/update', params=params, timeout=self.timeout)
        response.raise_for_status()
        return True

    def read_int(self, pin):
        if not self.enabled():
            return None
        try:
            response = self.session.get(
                self.BASE_URL + '/get',
                params={'token': self.token, 'pin': pin},
                timeout=self.timeout,
            )
            response.raise_for_status()
            raw = response.json()
            value = raw[0] if isinstance(raw, list) and raw else raw
            return int(float(value))
        except Exception:
            return None
