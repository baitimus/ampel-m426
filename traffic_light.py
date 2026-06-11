from machine import Pin
 
 
class TrafficLight:
    """controls the 3 leds on the lights."""
 
    def __init__(self, name: str, pin_red: int, pin_yellow: int, pin_green: int):
        self.name = name
        self._red    = Pin(pin_red,    Pin.OUT)
        self._yellow = Pin(pin_yellow, Pin.OUT)
        self._green  = Pin(pin_green,  Pin.OUT)
        self.all_off()
 
    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------
 
    def _set(self, red: bool, yellow: bool, green: bool):
        self._red.value(1 if red    else 0)
        self._yellow.value(1 if yellow else 0)
        self._green.value(1 if green   else 0)
 
    # ----------------------------------------------------------
    # Named light phases
    # ----------------------------------------------------------
 
    def show_red(self):
        self._set(red=True, yellow=False, green=False)
 
    def show_red_yellow(self):
        self._set(red=True, yellow=True, green=False)
 
    def show_green(self):
        self._set(red=False, yellow=False, green=True)
 
    def show_yellow(self):
        self._set(red=False, yellow=True, green=False)
 
    def all_off(self):
        self._set(red=False, yellow=False, green=False)
 