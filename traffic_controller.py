import utime
import config
from traffic_light  import TrafficLight
from states         import (CarRedState, CarRedYellowState,
                             CarGreenState, CarYellowState,
                             PedestrianRedState, PedestrianGreenState)

from observer       import TrafficSubject
 
 
class TrafficController(TrafficSubject):
    """Main controller that drives both traffic lights."""
 
    def __init__(self):
        super().__init__()
 
        # Physical lights
        self._car_light = TrafficLight(
            "cars",
            config.CAR_PIN_RED, config.CAR_PIN_YELLOW, config.CAR_PIN_GREEN
        )
        self._ped_light = TrafficLight(
            "pedestrians",
            config.PED_PIN_RED, config.PED_PIN_YELLOW, config.PED_PIN_GREEN
        )
 
        # Current state objects
        self._car_state = CarGreenState()
        self._ped_state = PedestrianRedState()
 
        # Apply initial LED states
        self._car_state.enter(self._car_light)
        self._ped_state.enter(self._ped_light)
 
        # Timestamp when the current state was entered
        self._car_state_entered_at  = utime.time()
        self._ped_state_entered_at  = utime.time()
 
        # Request flags set by the web server
        self._pedestrian_requested = False
        self._car_requested        = False
 
        # Safety-delay tracking: when a ped request arrives while
        # cars are green, we start a countdown before switching
        self._ped_interrupt_triggered_at = None
 
        # Broadcast initial states
        self.notify_observers("cars",        self._car_state.NAME)
        self.notify_observers("pedestrians", self._ped_state.NAME)
 
    # ----------------------------------------------------------
    # Public API for the web server
    # ----------------------------------------------------------
 
    def request_pedestrian_green(self):
        """Called when a pedestrian presses the button on the web page."""
        self._pedestrian_requested = True
 
    def request_car_green(self):
        """Called when a car driver presses the button on the web page."""
        self._car_requested = True
 
    def get_status(self) -> dict:
        """Returns current state info for the web UI observer."""
        return {
            "cars":        self._car_state.NAME,
            "pedestrians": self._ped_state.NAME,
            "ped_pending": self._pedestrian_requested,
            "car_pending": self._car_requested,
        }
 
    # ----------------------------------------------------------
    # Main loop — call this repeatedly from main.py
    # ----------------------------------------------------------
 
    def tick(self):
        """Non-blocking tick. Call as often as possible in the main loop."""
        now = utime.time()
 
        # ── Handle pedestrian interrupt request ─────────────────
        if self._pedestrian_requested:
            if isinstance(self._car_state, CarGreenState):
                # Start safety delay countdown on first detection
                if self._ped_interrupt_triggered_at is None:
                    self._ped_interrupt_triggered_at = now
 
                # After safety delay: switch cars to yellow → red
                if now - self._ped_interrupt_triggered_at >= config.PEDESTRIAN_SAFETY_DELAY:
                    self._transition_car(CarYellowState())
                    self._ped_interrupt_triggered_at = None
 
            elif isinstance(self._car_state, CarRedState):
                # Cars are already red — give pedestrians green now
                self._pedestrian_requested = False
                self._car_requested        = False  # consume any car req too
                self._transition_ped(PedestrianGreenState())
 
        # ── Car light normal cycle ───────────────────────────────
        car_elapsed = now - self._car_state_entered_at
 
        if isinstance(self._car_state, CarYellowState):
            if car_elapsed >= self._car_state.duration_seconds:
                self._transition_car(CarRedState())
 
        elif isinstance(self._car_state, CarRedYellowState):
            if car_elapsed >= self._car_state.duration_seconds:
                self._transition_car(CarGreenState())
 
        elif isinstance(self._car_state, CarGreenState):
            if car_elapsed >= self._car_state.duration_seconds:
                # Normal end of green — switch to yellow
                self._transition_car(CarYellowState())
 
        # CarRedState is held until pedestrians are done (handled below)
 
        # ── Pedestrian light cycle ───────────────────────────────
        ped_elapsed = now - self._ped_state_entered_at
 
        if isinstance(self._ped_state, PedestrianGreenState):
            if ped_elapsed >= self._ped_state.duration_seconds:
                # Pedestrian green is over — go back to red
                self._transition_ped(PedestrianRedState())
                # Give cars the red+yellow → green transition
                self._transition_car(CarRedYellowState())
 
        # ── Handle car request (only when pedestrians are red) ───
        if self._car_requested and isinstance(self._ped_state, PedestrianRedState):
            if isinstance(self._car_state, CarRedState):
                self._car_requested = False
                self._transition_car(CarRedYellowState())
 
    # ----------------------------------------------------------
    # Private state transition helpers
    # ----------------------------------------------------------
 
    def _transition_car(self, new_state):
        self._car_state = new_state
        self._car_state.enter(self._car_light)
        self._car_state_entered_at = utime.time()
        self.notify_observers("cars", self._car_state.NAME)
 
    def _transition_ped(self, new_state):
        # Safety guard: never allow both green simultaneously
        if isinstance(new_state, PedestrianGreenState):
            if not isinstance(self._car_state, CarRedState):
                return  # Refuse — cars are not red yet
 
        self._ped_state = new_state
        self._ped_state.enter(self._ped_light)
        self._ped_state_entered_at = utime.time()
        self.notify_observers("pedestrians", self._ped_state.NAME)
 