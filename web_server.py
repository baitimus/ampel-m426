import socket
import network
import config
from observer import TrafficObserver
 
 
# ----------------------------------------------------------
# HTML template (inline, minimal, mobile-friendly)
# ----------------------------------------------------------
 
def _build_html(status: dict) -> str:
    car_color = {
        "RED":        "#e74c3c",
        "RED_YELLOW": "#e67e22",
        "GREEN":      "#2ecc71",
        "YELLOW":     "#f1c40f",
    }.get(status["cars"], "#888")
 
    ped_color = {
        "RED":   "#e74c3c",
        "GREEN": "#2ecc71",
    }.get(status["pedestrians"], "#888")
 
    ped_pending_badge = "<span class='badge'>Anfrage läuft...</span>" if status["ped_pending"] else ""
    car_pending_badge = "<span class='badge'>Anfrage läuft...</span>" if status["car_pending"] else ""
 
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="2">
  <title>Ampelsteuerung</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: Arial, sans-serif;
      background: #1a1a2e;
      color: #eee;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      min-height: 100vh;
    }}
    h1 {{ font-size: 1.6rem; margin-bottom: 24px; color: #fff; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      width: 100%;
      max-width: 480px;
    }}
    .card {{
      background: #16213e;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      border: 2px solid #0f3460;
    }}
    .card h2 {{ font-size: 1rem; margin-bottom: 12px; color: #a0aec0; }}
    .light-circle {{
      width: 64px;
      height: 64px;
      border-radius: 50%;
      margin: 0 auto 10px;
      border: 3px solid rgba(255,255,255,0.15);
    }}
    .state-label {{ font-size: 0.85rem; font-weight: bold; }}
    .badge {{
      display: inline-block;
      background: #f39c12;
      color: #000;
      border-radius: 6px;
      padding: 2px 6px;
      font-size: 0.7rem;
      margin-top: 6px;
    }}
    .btn-section {{
      margin-top: 28px;
      width: 100%;
      max-width: 480px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    button {{
      padding: 16px 8px;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      transition: opacity 0.2s;
    }}
    button:active {{ opacity: 0.7; }}
    .btn-ped  {{ background: #2ecc71; color: #000; }}
    .btn-car  {{ background: #3498db; color: #fff; }}
    .footer {{ margin-top: 20px; font-size: 0.7rem; color: #4a5568; }}
  </style>
</head>
<body>
  <h1>🚦 Ampelsteuerung</h1>
 
  <div class="grid">
    <div class="card">
      <h2>Autos</h2>
      <div class="light-circle" style="background:{car_color};"></div>
      <div class="state-label">{status['cars']}</div>
      {car_pending_badge}
    </div>
    <div class="card">
      <h2>Fussgänger</h2>
      <div class="light-circle" style="background:{ped_color};"></div>
      <div class="state-label">{status['pedestrians']}</div>
      {ped_pending_badge}
    </div>
  </div>
 
  <div class="btn-section">
    <form method="POST" action="/pedestrian">
      <button class="btn-ped" type="submit">🚶 Ich möchte grün!</button>
    </form>
    <form method="POST" action="/car">
      <button class="btn-car" type="submit">🚗 Ich möchte grün!</button>
    </form>
  </div>
 
  <p class="footer">Seite aktualisiert sich alle 2 Sekunden</p>
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
 
    # TrafficObserver callback — just keep reference (status fetched live)
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
        """Check for an incoming connection and handle it if one is ready.
        Returns immediately if no client is waiting (non-blocking)."""
        if self._socket is None:
            return
 
        try:
            client, addr = self._socket.accept()
        except OSError:
            return  # No client waiting — perfectly normal
 
        try:
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
                # Default: serve the main page
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