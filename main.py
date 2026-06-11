import utime
from traffic_controller import TrafficController
from web_server         import WebServer
 
 
def main():
    print("[Main] Booting Ampelsteuerung...")
 
    controller = TrafficController()
    server     = WebServer(controller)
 
    server.start()
 
    print("[Main] Entering main loop.")
 
    while True:
        # Handle one pending HTTP request (non-blocking)
        server.handle_pending_request()
 
        # Advance the traffic light state machine
        controller.tick()
        
        # Small sleep to avoid busy-looping and give the Pico W time
        # to process Wi-Fi packets
        utime.sleep_ms(100)
 
 
main()