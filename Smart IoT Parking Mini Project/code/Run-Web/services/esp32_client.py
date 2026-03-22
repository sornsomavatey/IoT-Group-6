import requests


class Esp32Client:
    def __init__(self, base_url, timeout=3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _get_json(self, path):
        response = requests.get(self.base_url + path, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def status(self):
        payload = self._get_json('/api/status')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 status unavailable')
        return payload.get('data', {})

    def gate_open(self):
        payload = self._get_json('/gate/open')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 gate open failed')
        return payload.get('data', {})

    def gate_close(self):
        payload = self._get_json('/gate/close')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 gate close failed')
        return payload.get('data', {})

    def exit_open(self):
        payload = self._get_json('/exit/open')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 exit open failed')
        return payload.get('data', {})

    def exit_close(self):
        payload = self._get_json('/exit/close')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 exit close failed')
        return payload.get('data', {})


    def light_on(self):
        payload = self._get_json('/light/on')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 light on failed')
        return payload.get('data', {})

    def light_off(self):
        payload = self._get_json('/light/off')
        if not payload.get('ok'):
            raise RuntimeError('ESP32 light off failed')
        return payload.get('data', {})
