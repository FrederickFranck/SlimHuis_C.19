#!/usr/bin/env python3

'''
Met dit programma kan je relays bedienen via drukknoppen
De GPIO pins waar de knoppen en de relais zijn aangesloten geef je op in
het config.toml bestand
'''

__author__ = "Frédèrick Franck"
__version__ = "1.0.0"
__license__ = "MIT"
__email__ = "frederick.franck@student.kdg.be"

import time
from gpiozero import DigitalOutputDevice
from gpiozero import Button
import toml
from enum import Enum


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
def toggle_relay(relay, buttonState):
    if(buttonState.value == 1):
        relay.off() if relay.value else relay.on()
        time.sleep(0.25)


# Geeft de staat van de button terug
def check_button(button):
    # TODO : Aanvullen voor de andere buttonstates
    if(button.is_pressed):
        return ButtonState.singlePress
    return ButtonState.notPressed


# Gaat voor elke knop nakijken of er gedrukt is
def loop():
    while True:
        for button, relay in zip(buttons, relays):
            toggle_relay(relay, check_button(button))


# Verschillende buttonstates voor opdracht 2
class ButtonState(Enum):
    notPressed = -1
    hold = 0
    singlePress = 1
    doublePress = 2
    triplePress = 3


if __name__ == "__main__":
    main()
