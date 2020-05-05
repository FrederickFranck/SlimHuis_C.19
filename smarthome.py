#!/usr/bin/env python3
'''
Met dit programma kan je relays bedienen via drukknoppen
De GPIO pins waar de knoppen en de relais zijn aangesloten geef je op in
het config.toml bestand
'''

__author__ = "Frédèrick Franck"
__version__ = "1.2.0"
__license__ = "MIT"
__email__ = "frederick.franck@student.kdg.be"

import time
import datetime
from enum import Enum
from gpiozero import DigitalOutputDevice
from gpiozero import Button
import toml
import threading


# GPIO PINS LADEN UIT DE CONFIG
CONFIG = toml.load('config.toml')
BUTTON_PINS = CONFIG.get("GPIO").get("Buttons")
RELAY_PINS = CONFIG.get("GPIO").get("Relays")


# LISTS
buttons = []
relays = []

# COUNTER
# een lijst die voor elke knop het aantal knop drukken gaat bijhouden
press_count = []


# Maak een lijst aan met buttons en stelt de event handler functie in
def initialize_buttons():
    global buttons
    for pin in BUTTON_PINS:
        buttons.append(Button(pin=pin))
        press_count.append(0)
    for btn in buttons:
        btn.when_pressed = button_is_pressed


# Event handler functie voor als de knop ingedrukt wordt
def button_is_pressed(button):
    global press_count
    press_count[buttons.index(button)] += 1


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
def check_button(index):
    button = buttons[index]
    relay = relays[index]
    timeout = 1.5
    global press_count
    press_count[index] = 0
    if(button.is_pressed):
        start_time = now()
        while(button.is_pressed):
            # Als de knop voor langer dan een halve seconde ingedrukt blijft
            if((get_elapsed_seconds(start_time)) >= 0.5):
                print("Hold")

                new_thread = threading.Thread(
                                            target=update_relay,
                                            args=(relay, ButtonState.HOLD,),
                                            daemon=True,
                                            name=("hold {}".format(relay.pin)))

                new_thread.start()
                return ButtonState.HOLD

        # Timout waarin de knop 2 of 3 keer ingedrukt kan worden
        while((get_elapsed_seconds(start_time)) < timeout):
            if(press_count[index] == 3):
                print("Triple Press")

                new_thread = threading.Thread(
                                    target=update_relay,
                                    args=(relay, ButtonState.TRIPLE_PRESS,),
                                    daemon=True,
                                    name=("triple press {}".format(relay.pin)))

                new_thread.start()
                return ButtonState.TRIPLE_PRESS

        if(((get_elapsed_seconds(start_time)) >= timeout)):
            if(press_count[index] == 1):
                print("One Press")

                new_thread = threading.Thread(
                                    target=update_relay,
                                    args=(relay, ButtonState.SINGLE_PRESS,),
                                    daemon=True,
                                    name=("one press {}".format(relay.pin)))

                new_thread.start()
                return ButtonState.SINGLE_PRESS

            if(press_count[index] == 2):
                print("Double Press")

                new_thread = threading.Thread(
                                    target=update_relay,
                                    args=(relay, ButtonState.DOUBLE_PRESS,),
                                    daemon=True,
                                    name=("double press {}".format(relay.pin)))

                new_thread.start()
                return ButtonState.DOUBLE_PRESS

    return ButtonState.NOT_PRESSED


# Past de relay aan adhv de staat van de knop
def update_relay(relay, button_state):
    if(button_state == ButtonState.SINGLE_PRESS):
        toggle_relay(relay)
        return

    if(check_relay(relay)):  # relay is on
        if(button_state == ButtonState.DOUBLE_PRESS):
            switch_all_off()
            return

        elif(button_state == ButtonState.TRIPLE_PRESS):
            temporary_toggle_all(10)
            return

        elif(button_state == ButtonState.HOLD):
            temporary_toggle_relay(relay, 10)
            return
    else:                    # relay is off
        if(button_state == ButtonState.DOUBLE_PRESS):
            switch_all_on()
            return

        elif(button_state == ButtonState.TRIPLE_PRESS):
            temporary_toggle_all(25, True, 5)
            return

        elif(button_state == ButtonState.HOLD):
            temporary_toggle_relay(relay, 25, True, 5)
            return


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
    if(warning and check_relay(relay)):
        blink(relay, warning_time)
    relay.off()


# Zet alle relays aan voor een bepaalde tijd als de warning aanstaat gaan
# de relays na de opgegeven tijd een aantal seconden knipperen
def temporary_toggle_all(seconds, warning=False, warning_time=0):
    for relay in relays:
        new_thread = threading.Thread(
                target=temporary_toggle_relay,
                args=(relay, seconds, warning, warning_time),
                daemon=True, name='all on {}'.format(relay.pin))

        new_thread.start()


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
        for index in range(len(buttons)):
            check_button(index)


# Main functie
def main():
    try:
        initialize_buttons()
        initialize_relays()
        for t in threading.enumerate():
            print(t.name)
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
