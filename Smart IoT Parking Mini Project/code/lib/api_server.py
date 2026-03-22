import socket
import json


class ApiServer:
    def __init__(self, controller, port=80):
        self.controller = controller
        self.port = port
        self.server_socket = None

    def start(self):
        if self.server_socket:
            return True
        try:
            addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(addr)
            sock.listen(3)
            sock.settimeout(0.001)
            self.server_socket = sock
            print("ESP32 API listening on port", self.port)
            return True
        except Exception as exc:
            print("Server start error:", exc)
            self.server_socket = None
            return False

    def _send_json(self, client, payload, status="200 OK"):
        try:
            body = json.dumps(payload)
            headers = (
                "HTTP/1.1 {}\r\n"
                "Content-Type: application/json\r\n"
                "Cache-Control: no-store\r\n"
                "Connection: close\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Content-Length: {}\r\n\r\n"
            ).format(status, len(body))
            client.send(headers.encode())
            client.send(body.encode())
        except Exception as exc:
            print("HTTP send error:", exc)

    def _request_path(self, req_bytes):
        try:
            line = req_bytes.split(b"\r\n", 1)[0]
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].decode()
        except Exception:
            pass
        return "/"

    def handle_once(self):
        if not self.server_socket:
            return
        try:
            client, _ = self.server_socket.accept()
        except OSError:
            return
        except Exception as exc:
            print("Accept error:", exc)
            return

        try:
            req = client.recv(512)
            if not req:
                return
            path = self._request_path(req)
            if path in ("/", "/api/status", "/status"):
                self._send_json(client, {"ok": True, "data": self.controller.get_status()})
            elif path == "/health":
                self._send_json(client, {"ok": True, "status": "running"})
            elif path == "/gate/open":
                self.controller.open_entry_gate("api")
                self._send_json(client, {"ok": True, "message": "entry_gate_opened", "data": self.controller.get_status()})
            elif path == "/gate/close":
                self.controller.close_entry_gate("api")
                self._send_json(client, {"ok": True, "message": "entry_gate_closed", "data": self.controller.get_status()})
            elif path == "/exit/open":
                self.controller.open_exit_gate("api")
                self._send_json(client, {"ok": True, "message": "exit_gate_opened", "data": self.controller.get_status()})
            elif path == "/exit/close":
                self.controller.close_exit_gate("api")
                self._send_json(client, {"ok": True, "message": "exit_gate_closed", "data": self.controller.get_status()})
            elif path == "/light/on":
                self.controller.turn_light_on("api")
                self._send_json(client, {"ok": True, "message": "light_on", "data": self.controller.get_status()})
            elif path == "/light/off":
                self.controller.turn_light_off("api")
                self._send_json(client, {"ok": True, "message": "light_off", "data": self.controller.get_status()})
            else:
                self._send_json(client, {"ok": False, "message": "not_found", "path": path}, status="404 Not Found")
        except Exception as exc:
            print("Handle HTTP error:", exc)
        finally:
            try:
                client.close()
            except Exception:
                pass
