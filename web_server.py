import socket
import network
import config
from observer import TrafficObserver

# ----------------------------------------------------------
# HTML template (Clean, tactile, industrial design)
# ----------------------------------------------------------

def _build_html(status: dict) -> str:
    # Map traffic light states to clean CSS classes
    car_color_class = {
        "RED": "bg-red",
        "RED_YELLOW": "bg-orange",
        "GREEN": "bg-green",
        "YELLOW": "bg-yellow",
    }.get(status["cars"], "")

    ped_color_class = {
        "RED": "bg-red",
        "GREEN": "bg-green",
    }.get(status["pedestrians"], "")

    ped_pending = "<div class='pending'>Warte auf Grün...</div>" if status["ped_pending"] else ""
    car_pending = "<div class='pending'>Warte auf Grün...</div>" if status["car_pending"] else ""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="2">
  <title>Ampelsteuerung</title>
  <style>
    /* Reset & Typography */
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
      background-color: #e4e4e7; /* Very light cool gray */
      color: #18181b; /* Near black */
      max-width: 600px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }}
    h1 {{
      font-size: 1.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 3px solid #18181b;
      padding-bottom: 0.5rem;
      margin-bottom: 2rem;
    }}
    
    /* Layout */
    .panel-container {{
      display: flex;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }}
    @media (max-width: 450px) {{
      .panel-container {{ flex-direction: column; }}
    }}
    
    /* Cards (Tactile, flat design) */
    .panel {{
      background: #ffffff;
      border: 3px solid #18181b;
      border-radius: 4px;
      padding: 1.5rem;
      flex: 1;
      text-align: center;
      box-shadow: 6px 6px 0px #18181b; /* Hard solid shadow */
    }}
    .panel h2 {{
      font-size: 1.1rem;
      margin-bottom: 1rem;
    }}
    
    /* Traffic Lights */
    .light-circle {{
      width: 70px;
      height: 70px;
      border-radius: 50%;
      border: 4px solid #18181b;
      margin: 0 auto 1rem auto;
      background-color: #d4d4d8; /* Default off color */
    }}
    
    /* Solid colors, no gradients */
    .bg-red {{ background-color: #ef4444; }}
    .bg-orange {{ background-color: #f97316; }}
    .bg-yellow {{ background-color: #eab308; }}
    .bg-green {{ background-color: #22c55e; }}

    .state-text {{ font-weight: 700; font-size: 1.2rem; }}
    .pending {{ color: #ea580c; font-size: 0.85rem; font-weight: bold; margin-top: 0.5rem; }}

    /* Action Buttons */
    .actions {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}
    button {{
      width: 100%;
      background-color: #ffffff;
      color: #18181b;
      border: 3px solid #18181b;
      padding: 1.25rem;
      font-size: 1rem;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
      box-shadow: 4px 4px 0px #18181b; /* Hard shadow */
      transition: transform 0.1s, box-shadow 0.1s;
      text-transform: uppercase;
    }}
    /* The physical click effect */
    button:active {{
      transform: translate(4px, 4px);
      box-shadow: 0px 0px 0px #18181b;
    }}
    button:hover {{
      background-color: #f4f4f5;
    }}

    .footer {{
      margin-top: 2rem;
      text-align: center;
      font-size: 0.8rem;
      color: #52525b;
      font-weight: 500;
    }}
  </style>
</head>
<body>
  <h1>Ampelsteuerung</h1>

  <div class="panel-container">
    <div class="panel">
      <h2>Autos</h2>
      <div class="light-circle {car_color_class}"></div>
      <div class="state-text">{status['cars']}</div>
      {car_pending}
    </div>
    
    <div class="panel">
      <h2>Fussgänger</h2>
      <div class="light-circle {ped_color_class}"></div>
      <div class="state-text">{status['pedestrians']}</div>
      {ped_pending}
    </div>
  </div>

  <div class="actions">
    <form method="POST" action="/pedestrian">
      <button type="submit">Fussgänger: Grün anfordern</button>
    </form>
    <form method="POST" action="/car">
      <button type="submit">Auto: Grün anfordern</button>
    </form>
  </div>

  <p class="footer">Status-Update alle 2 Sekunden</p>
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