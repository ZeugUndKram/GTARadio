import os
import sys
import time
import logging
import spidev as SPI
# Adjust the path to point to the top-level directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from evdev import UInput, ecodes as e
import subprocess
import threading

from display import display_image, display_image_delay
from radio import play_radio

folder_index = 4

image_index = 1
channel_index = 0
song_index = 0

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

PIN_CLK = 16
PIN_DT = 15
BUTTON_PIN = 14

GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)


# Benötigte Variablen werden initialisiert
Counter = 0
Richtung = True
PIN_CLK_LETZTER = 0
PIN_CLK_AKTUELL = 0
delayTime = 0.02


# Initiales Auslesen des Pin_CLK
PIN_CLK_LETZTER = GPIO.input(PIN_CLK)

last_reset_time = 0
reset_pressed = False

display_image(folder_index, image_index)
play_radio(folder_index, image_index)


# Diese AusgabeFunktion wird bei Signaldetektion ausgefuehrt
def ausgabeFunktion(null):
    global image_index, folder_size, folder_size
    PIN_CLK_AKTUELL = GPIO.input(PIN_CLK)

    if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:
        if folder_index == 0:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 9:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True;
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 9
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")
        if folder_index == 1:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 9:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True;
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 9
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")
        if folder_index == 2:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 11:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True;
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 11
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")
        if folder_index == 3:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 20:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True;
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 20
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")
        if folder_index == 4:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 18:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True;
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 18
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")

def CounterReset(null):
    global last_reset_time, folder_index, Counter

    current_time = time.time()
    if current_time - last_reset_time < 2:
        folder_index += 1
        if folder_index > 4:
            folder_index = 0
        threading.Thread(target=display_image_delay, args=(folder_index,image_index)).start()
    Counter = 0
    display_image(folder_index, 0)
    last_reset_time = current_time
    print("a")

# CallBack-Option vom GPIO Python Modul initialisiert
GPIO.add_event_detect(PIN_CLK, GPIO.FALLING, callback=ausgabeFunktion, bouncetime=100)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=CounterReset, bouncetime=300)



try:

    while True:
        user_input = input("Press 'L' for previous image, 'A' to change folder, 'R' for next image, or 'Q' to quit: ")

        if user_input == 'q':
            break
        elif user_input == 'l':
            break
        elif user_input == 'r':
            break

        #Radioswitch
        elif user_input == 'a':
            break

        time.sleep(delayTime)

except IOError as e:
    logging.error(e)
except KeyboardInterrupt:
    pass
finally:
    logging.info("quit:")

