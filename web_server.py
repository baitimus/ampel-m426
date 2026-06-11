import socket
import network
import config
from observer import TrafficObserver
 
# ----------------------------------------------------------
# HTML template (inline, minimal, no styling)
# ----------------------------------------------------------
 
def _build_html(status: dict) -> str:
    ped_pending = " (Anfrage läuft...)" if status["ped_pending"] else ""
    car_pending = " (Anfrage läuft...)" if status["car_pending"] else ""
 
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="2">
  <title>Ampelsteuerung</title>
</head>
<body>
  <h1>Ampelsteuerung</h1>
 
  <h2>Autos</h2>
  <p>Status: <strong>{status['cars']}</strong>{car_pending}</p>
 
  <h2>Fussgaenger</h2>
  <p>Status: <strong>{status['pedestrians']}</strong>{ped_pending}</p>
 
  <hr>
 
  <form method="POST" action="/pedestrian">
    <button type="submit">Fussgaenger: Ich moechte gruen!</button>
  </form>
  
  <br>
  
  <form method="POST" action="/car">
    <button type="submit">Auto: Ich moechte gruen!</button>
  </form>
 
  <p><small>Seite aktualisiert sich alle 2 Sekunden</small></p>
</body>
</html>"""
 
# ----------------------------------------------------------
# WebServer class
# ----------------------------------------------------------
 
class WebServer(TrafficObserver):
    """HTTP server that also observes traffic light state changes."""
 
    def __init__(self, controller):
        self._controller = controller
        self._socket = None
        self._controller.register_observer(self)
 
    def on_state_changed(self, light_name: str, state_name: str):
        pass  # Status is always fetched fresh from controller.get_status()
 
    def start(self):
        """Set up the Wi-Fi access point and open the TCP socket."""
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=config.WIFI_SSID, password=config.WIFI_PASSWORD)
        ap.active(True)
 
        while not ap.active():
            pass
 
        print(f"[WebServer] AP active. Connect to SSID: {config.WIFI_SSID}")
        print(f"[WebServer] IP: {ap.ifconfig()[0]}")
 
        addr = socket.getaddrinfo("0.0.0.0", config.SERVER_PORT)[0][-1]
        self._socket = socket.socket()
        self._socket.bind(addr)
        self._socket.listen(1)
        self._socket.setblocking(False)  # Non-blocking so tick() is not stalled
 
        print(f"[WebServer] Listening on port {config.SERVER_PORT}")
 
    def handle_pending_request(self):
        """Check for an incoming connection and handle it if one is ready."""
        if self._socket is None:
            return
 
        try:
            client, addr = self._socket.accept()
        except OSError:
            return  # No client waiting
 
        try:
            client.settimeout(1.0)
            raw_request = client.recv(1024).decode("utf-8")
            first_line  = raw_request.split("\r\n")[0] if raw_request else ""
            method, path = self._parse_request_line(first_line)
 
            if method == "POST" and path == "/pedestrian":
                self._controller.request_pedestrian_green()
                self._send_redirect(client, "/")
 
            elif method == "POST" and path == "/car":
                self._controller.request_car_green()
                self._send_redirect(client, "/")
 
            elif path == "/status":
                self._send_json(client, self._controller.get_status())
 
            else:
                html = _build_html(self._controller.get_status())
                self._send_html(client, html)
 
        except Exception as error:
            print(f"[WebServer] Error handling request: {error}")
        finally:
            client.close()
 
    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------
 
    def _parse_request_line(self, line: str):
        parts = line.split(" ")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return "GET", "/"
 
    def _send_html(self, client, html: str):
        response = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "\r\n"
        ) + html
        client.send(response.encode("utf-8"))
 
    def _send_redirect(self, client, location: str):
        response = (
            f"HTTP/1.0 303 See Other\r\n"
            f"Location: {location}\r\n"
            "\r\n"
        )
        client.send(response.encode("utf-8"))
 
    def _send_json(self, client, data: dict):
        body = str(data).replace("'", '"').replace("True", "true").replace("False", "false")
        response = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "\r\n"
        ) + body
        client.send(response.encode("utf-8"))