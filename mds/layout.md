# Ampel Board Layout

This document describes the GPIO pin layout and wiring for the traffic light (Ampel) connections on the Raspberry Pi Pico W board.

## Visualization

```text
                                  Pico W
                                ┌────────┐
                          Pin 1 ┤        ├ Pin 40
                          Pin 2 ┤        ├ Pin 39
                          Pin 3 ┤        ├ Pin 38
                          Pin 4 ┤        ├ Pin 37
                          Pin 5 ┤        ├ Pin 36
                          Pin 6 ┤        ├ Pin 35
           Ampel 1        Pin 7 ┤        ├ Pin 34
           (Autos)              │        │
         [ GND ]------ Pin 8 GND┤        ├ Pin 33
       [ R (rot) ]---- Pin 9 GP6┤        ├ Pin 32
      [ Y (gelb) ]--- Pin 10 GP7┤        ├ Pin 31
      [ G (grün) ]--- Pin 11 GP8┤        ├ Pin 30
                                │        ├ Pin 29 GP22
                                │        ├ Pin 28 GND
                                │        │                    Ampel 2
                                │        ├ Pin 27 GP21      (Fussgänger)
                                │        ├ Pin 26 GP20 ------ [ G (grün) ]
                                │        ├ Pin 25 GP19 ------ [ Y (gelb) ]
                                │        ├ Pin 24 GP18 ------ [ R (rot) ]
                                │        ├ Pin 23 GND ------- [ GND ]
                                │        ├ Pin 22 GP17
                                │        ├ Pin 21 GP16
                                └────────┘
```

**Wiring Notes:**
* Each LED needs a 220Ω–330Ω resistor in series (between pin and LED).
* GP17 (Pin 22) on Ampel 2 is unused (no yellow on pedestrian light in code).

## Pin Mappings

### Ampel 1: Autos (Cars)
* **Ground (GND):** Pin 8 (GND)
* **Red Light:** Pin 9 (GP6)
* **Yellow Light:** Pin 10 (GP7)
* **Green Light:** Pin 11 (GP8)

### Ampel 2: Fußgänger (Pedestrians)
* **Ground (GND):** Pin 23 (GND)
* **Red Light:** Pin 24 (GP18)
* **Yellow Light:** Pin 25 (GP19)
* **Green Light:** Pin 26 (GP20)
