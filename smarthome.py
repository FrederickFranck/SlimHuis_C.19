#!/usr/bin/env python3

'''
Met dit programma kan je relays bedienen via drukknoppen
De GPIO pins waar de knoppen en de relais zijn aangesloten geef je op in
het config.toml bestand
'''

__author__ = "Frédèrick Franck"
__version__ = "1.0.1"
__license__ = "MIT"
__email__ = "frederick.franck@student.kdg.be"

import time
import datetime
from enum import Enum
from gpiozero import DigitalOutputDevice
from gpiozero import Button
import toml




# GPIO PINS LADEN UIT DE CONFIG
CONFIG = toml.load('config.toml')
BUTTON_PINS = CONFIG.get("GPIO").get("Buttons")
RELAY_PINS = CONFIG.get("GPIO").get("Relays")


# LISTS
buttons = []
relays = []


# Main functie
def main():
    try:
        initialize_buttons()
        initialize_relays()
        loop()
    except KeyboardInterrupt:
        exit()


# Maak een lijst aan met buttons
def initialize_buttons():
    global buttons
    for pin in BUTTON_PINS:
        buttons.append(Button(pin=pin, bounce_time=0.25))


# Maak een lijst aan met Relays
def initialize_relays():
    global relays
    for pin in RELAY_PINS:
        relays.append(DigitalOutputDevice(pin=pin, active_high=True,
                                          initial_value=False))


# Past de relay aan adhv de staat van de knop
def toggle_relay(relay, button):
    button_state = check_button(button)
    if(check_relay(relay)):  # relay is on
        if(button_state == ButtonState.SINGLE_PRESS):
            relay.off()

    else:                    # relay is off
        if(button_state == ButtonState.SINGLE_PRESS):
            relay.on()


# Geeft de staat van de relay terug
def check_relay(relay):
    return relay.value


# Geeft de staat van de button terug
def check_button(button):
    timeout = 2
    if(button.value):
        start_time = now()

        while(button.value):
            # Als de knop voor langer dan een halve seconde ingedrukt blijft
            if((get_seconds_delta(now(), start_time)) >= 0.5):
                print("seconds" + str((get_seconds_delta(now(), start_time))))
                print("hold")
                return ButtonState.HOLD

        # Timout waarin de knop 2 of 3 keer ingedrukt kan worden
        while((get_seconds_delta(now(), start_time)) <= timeout):
            if(button.value):
                # twee keer gedrukt
                while((get_seconds_delta(now(), start_time)) <= timeout):
                    if(button.value):
                        # drie keer gedrukt
                        print(start_time)
                        print("triple press")
                        return ButtonState.TRIPLE_PRESS
                print(start_time)
                print("double press")
                return ButtonState.DOUBLE_PRESS
        if(((get_seconds_delta(now(), start_time)) > timeout)):
            print(start_time)
            print("single press")
            return ButtonState.SINGLE_PRESS
    return ButtonState.NOT_PRESSED


# Geeft de huidige tijd als datetime object terug
def now():
    return datetime.datetime.now()


# Geeft het vershil tussen twee datetime objecten in seconden
def get_seconds_delta(datetime_end, datetime_start):
    return (datetime_end - datetime_start).total_seconds()


# Gaat voor elke knop nakijken of er gedrukt is
def loop():
    while True:
        for button, relay in zip(buttons, relays):
            toggle_relay(relay, button)


# Verschillende buttonstates voor opdracht 2
class ButtonState(Enum):
    NOT_PRESSED = -1
    HOLD = 0
    SINGLE_PRESS = 1
    DOUBLE_PRESS = 2
    TRIPLE_PRESS = 3


if __name__ == "__main__":
    main()
