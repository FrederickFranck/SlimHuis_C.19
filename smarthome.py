#!/usr/bin/env python3
'''
Met dit programma kan je relays bedienen via drukknoppen
De GPIO pins waar de knoppen en de relais zijn aangesloten geef je op in
het config.toml bestand
'''

__author__ = "Frédèrick Franck"
__version__ = "1.1.0"
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

# COUNTER
# Ik ga er van uit dat knoppen niet tegelijk ingedrukt worden
# als dit wel zo is moet er voor elke knop een aparte counter komen
press_count = 0


# Maak een lijst aan met buttons en stelt de event handler functie in
def initialize_buttons():
    global buttons
    for pin in BUTTON_PINS:
        buttons.append(Button(pin=pin))
    for btn in buttons:
        btn.when_pressed = button_is_pressed


# Event handler functie voor als de knop ingedrukt wordt
# Ik ga er van uit dat knoppen niet tegelijk ingedrukt worden
# als dit wel zo is moet er voor elke knop een aparte counter komen
def button_is_pressed(button):
    global counter
    counter += 1


# Maak een lijst aan met Relays
def initialize_relays():
    global relays
    for pin in RELAY_PINS:
        relays.append(DigitalOutputDevice(pin=pin, active_high=True,
                                          initial_value=False))


# Geeft de staat van de relay terug
def check_relay(relay):
    return relay.value


# Geeft de staat van de button terug
def check_button(button):
    timeout = 2
    global counter
    counter = 0
    if(button.is_pressed):
        start_time = now()
        while(button.is_pressed):
            # Als de knop voor langer dan een halve seconde ingedrukt blijft
            if((get_elapsed_seconds(start_time)) >= 0.5):
                print("seconds" + str((get_elapsed_seconds(start_time))))
                print("hold")
                return ButtonState.HOLD

        # Timout waarin de knop 2 of 3 keer ingedrukt kan worden
        while((get_elapsed_seconds(start_time)) < timeout):
            if(counter == 3):
                print("tripel")
                return ButtonState.TRIPLE_PRESS
        if(((get_elapsed_seconds(start_time)) >= timeout)):
            if(counter == 1):
                print("once")
                return ButtonState.SINGLE_PRESS
            if(counter == 2):
                print("twice")
                return ButtonState.DOUBLE_PRESS
    return ButtonState.NOT_PRESSED


# Past de relay aan adhv de staat van de knop
def update_relay(relay, button):
    button_state = check_button(button)
    if(button_state == ButtonState.SINGLE_PRESS):
        toggle_relay(relay)
    if(check_relay(relay)):  # relay is on
        if(button_state == ButtonState.DOUBLE_PRESS):
            switch_all_off()
        elif(button_state == ButtonState.TRIPLE_PRESS):
            temporary_toggle_all(10)
        elif(button_state == ButtonState.HOLD):
            temporary_toggle_relay(relay, 10)

    else:                    # relay is off
        if(button_state == ButtonState.DOUBLE_PRESS):
            switch_all_on()
        elif(button_state == ButtonState.TRIPLE_PRESS):
            temporary_toggle_all(25, True, 5)
        elif(button_state == ButtonState.HOLD):
            temporary_toggle_relay(relay, 25, True, 5)


# Geeft de huidige tijd als datetime object terug
def now():
    return datetime.datetime.now()


# Geeft het aantal seconden terug die verstrekent zijn vanaf de starttijd
def get_elapsed_seconds(datetime_start):
    return (now() - datetime_start).total_seconds()


# Zet de relay uit als hij aanstaat en aan als hij uitstaat
def toggle_relay(relay):
    relay.off() if relay.value else relay.on()


# Zet de relay aan voor een bepaalde tijd als de warning aanstaat gaat de relay
# na de opgegeven tijd een aantal seconden knipperen
def temporary_toggle_relay(relay, seconds, warning=False, warning_time=0):
    relay.on()
    start_time = now()
    while(get_elapsed_seconds(start_time) <= seconds):
        pass
    if(warning):
        blink(relay, warning_time)
    relay.off()


# Zet alle relays aan voor een bepaalde tijd als de warning aanstaat gaan
# de relays na de opgegeven tijd een aantal seconden knipperen
def temporary_toggle_all(seconds, warning=False, warning_time=0):
    for relay in relays:
        temporary_toggle_relay(relay, seconds, warning, warning_time)


# Knippert een relay voor een aantal seconden
def blink(relay, seconds):
    start_time = now()
    while(get_elapsed_seconds(start_time) <= seconds):
        relay.on()
        time.sleep(0.1)
        relay.off()
        time.sleep(0.1)


# Zet alle relays aan
def switch_all_on():
    for relay in relays:
        relay.on()


# Zet alle relays die aan staan uit
def switch_all_off():
    for relay in relays:
        if(relay.value):
            relay.off()


# Gaat voor elke knop nakijken of er gedrukt is
# en bestuurt de relays volgens de flowchart
def loop():
    while True:
        for button, relay in zip(buttons, relays):
            update_relay(relay, button)


# Main functie
def main():
    try:
        initialize_buttons()
        initialize_relays()
        loop()
    except KeyboardInterrupt:
        exit()


# Verschillende buttonstates als enum
class ButtonState(Enum):
    NOT_PRESSED = -1
    HOLD = 0
    SINGLE_PRESS = 1
    DOUBLE_PRESS = 2
    TRIPLE_PRESS = 3


if __name__ == "__main__":
    main()
