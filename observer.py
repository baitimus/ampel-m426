class TrafficObserver:
    """Base class for anything that observes traffic light state changes."""
 
    def on_state_changed(self, light_name: str, state_name: str):
        """Called whenever a traffic light transitions to a new state.
 
        Args:
            light_name: 'cars' or 'pedestrians'
            state_name: e.g. 'RED', 'RED_YELLOW', 'GREEN', 'YELLOW'
        """
        raise NotImplementedError
 
 
class TrafficSubject:
    """Mixin that gives any class the ability to register observers
    and broadcast state-change events."""
 
    def __init__(self):
        self._observers: list = []
 
    def register_observer(self, observer: TrafficObserver):
        self._observers.append(observer)
 
    def unregister_observer(self, observer: TrafficObserver):
        self._observers.remove(observer)
 
    def notify_observers(self, light_name: str, state_name: str):
        for observer in self._observers:
            observer.on_state_changed(light_name, state_name)
 