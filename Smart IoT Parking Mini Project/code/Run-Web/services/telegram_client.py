import requests


class TelegramClient:
    def __init__(self, bot_token, chat_id, timeout=3):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout = timeout
        self.last_update_id = None

    def enabled(self):
        return bool(self.bot_token and self.chat_id)

    def _request(self, method, **params):
        if not self.enabled():
            return None
        response = requests.get(
            'https://api.telegram.org/bot{}/{}'.format(self.bot_token, method),
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def send(self, text):
        if self.enabled():
            self._request('sendMessage', chat_id=self.chat_id, text=text)

    def get_updates(self):
        if not self.enabled():
            return []
        params = {'timeout': 1}
        if self.last_update_id is not None:
            params['offset'] = self.last_update_id + 1
        payload = self._request('getUpdates', **params) or {}
        result = payload.get('result', [])
        for item in result:
            self.last_update_id = item.get('update_id', self.last_update_id)
        return result
