class TrafficLightState:
    NAME = "UNKNOWN"
 
    def enter(self, light):
        """Activate the correct LEDs on the physical light."""
        raise NotImplementedError
 
    @property
    def duration_seconds(self) -> float:
        raise NotImplementedError
 
    def next_state(self) -> "TrafficLightState":
        raise NotImplementedError
 
    def __str__(self):
        return self.NAME
 
 
# ----------------------------------------------------------
# Car traffic light states
# ----------------------------------------------------------
 
class CarRedState(TrafficLightState):
    NAME = "RED"
 
    def enter(self, light):
        light.show_red()
 
    @property
    def duration_seconds(self):
        # Stays red until pedestrians are done; controller manages this
        return 9999  # Effectively infinite — controller overrides timing
 
    def next_state(self):
        return CarRedYellowState()
 
 
class CarRedYellowState(TrafficLightState):
    NAME = "RED_YELLOW"
 
    def enter(self, light):
        light.show_red_yellow()
 
    @property
    def duration_seconds(self):
        return config.PHASE_RED_YELLOW_DURATION
 
    def next_state(self):
        return CarGreenState()
 
 
class CarGreenState(TrafficLightState):
    NAME = "GREEN"
 
    def enter(self, light):
        light.show_green()
 
    @property
    def duration_seconds(self):
        return config.PHASE_GREEN_DURATION
 
    def next_state(self):
        return CarYellowState()
 
 
class CarYellowState(TrafficLightState):
    NAME = "YELLOW"
 
    def enter(self, light):
        light.show_yellow()
 
    @property
    def duration_seconds(self):
        return config.PHASE_YELLOW_DURATION
 
    def next_state(self):
        return CarRedState()
 

 
class PedestrianRedState(TrafficLightState):
    NAME = "RED"
 
    def enter(self, light):
        light.show_red()
 
    @property
    def duration_seconds(self):
        return 9999  # Stays red until a request comes in
 
    def next_state(self):
        return PedestrianGreenState()
 
 
class PedestrianGreenState(TrafficLightState):
    NAME = "GREEN"
 
    def enter(self, light):
        light.show_green()
 
    @property
    def duration_seconds(self):
        return config.PEDESTRIAN_GREEN_DURATION
 
    def next_state(self):
        return PedestrianRedState()