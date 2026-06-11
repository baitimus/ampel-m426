# --- Ampel 1 (Autos) GPIO pins ---
CAR_PIN_RED    = 6
CAR_PIN_YELLOW = 7
CAR_PIN_GREEN  = 8
 
# --- Ampel 2 (fuhsgenger) GPIO pins ---
PED_PIN_RED    = 18
PED_PIN_YELLOW = 19
PED_PIN_GREEN  = 20
 
# --- Timing (s) ---
PHASE_RED_YELLOW_DURATION  = 2   # Red+Yellow before going green
PHASE_GREEN_DURATION       = 10  # How long green lasts normally
PHASE_YELLOW_DURATION      = 3   # Yellow before red
PEDESTRIAN_SAFETY_DELAY    = 2   # Delay after request before cars switch
PEDESTRIAN_GREEN_DURATION  = 8   # How long pedestrians get green
 
# --- Wi-Fi--
WIFI_SSID     = "Ampel-Pico"
WIFI_PASSWORD = "ampel1234"
 
# --- Web server ---
SERVER_PORT = 80