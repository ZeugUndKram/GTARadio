import os
import sys
import time
import logging
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e
import subprocess
import threading

# Local imports
from lib import LCD_1inch28
from display import display_image, display_image_delay
from radio import play_radio

# --- Global state variables ---
folder_index = 0
image_index = 1
channel_index = 0
song_index = 0

# Raspberry Pi pin configuration
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Rotary encoder + button GPIO pins
PIN_CLK = 16
PIN_DT = 15
BUTTON_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Rotary encoder state
Counter = 0
Richtung = True
PIN_CLK_LETZTER = GPIO.input(PIN_CLK)   # Initial read of CLK pin
PIN_CLK_AKTUELL = 0
delayTime = 0.02

# Button press timing
last_reset_time = 0
reset_pressed = False

# Initial display + radio
display_image(folder_index, image_index)
play_radio(folder_index, image_index)


# --- Rotary encoder callback ---
def ausgabeFunktion(null):
    """
    Handles rotary encoder rotation:
    - Updates image_index depending on rotation direction
    - Wraps around valid range for each folder
    - Updates display and radio
    """
    global image_index, folder_size, folder_index, PIN_CLK_LETZTER

    PIN_CLK_AKTUELL = GPIO.input(PIN_CLK)

    # Only trigger when CLK changes
    if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:
        # --- Folder 0 ---
        if folder_index == 0:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:  # Rotate right
                image_index += 1
                if image_index > 9:  # Wrap around
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True
            else:  # Rotate left
                image_index -= 1
                if image_index < 1:
                    image_index = 9
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")

        # --- Folder 1 ---
        if folder_index == 1:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 9:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 9
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")

        # --- Folder 2 ---
        if folder_index == 2:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 11:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 11
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")

        # --- Folder 3 ---
        if folder_index == 3:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 20:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 20
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")

        # --- Folder 4 ---
        if folder_index == 4:
            if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                image_index += 1
                if image_index > 18:
                    image_index = 1
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                print("r")
                Richtung = True
            else:
                image_index -= 1
                if image_index < 1:
                    image_index = 18
                display_image(folder_index, image_index)
                play_radio(folder_index, image_index)
                Richtung = False
                print("l")


# --- Button callback ---
def CounterReset(null):
    """
    Handles button presses:
    - Single press = reset counter
    - Double press (<2s) = switch to next folder
    """
    global last_reset_time, folder_index, Counter, image_index

    current_time = time.time()

    # Double press within 2s → change folder
    if current_time - last_reset_time < 2:
        folder_index += 1
        if folder_index > 4:
            folder_index = 0
        threading.Thread(
            target=display_image_delay,
            args=(folder_index, image_index)
        ).start()
        Counter = 0
        display_image(folder_index, 0)

    last_reset_time = current_time
    print("a")


# --- Setup GPIO event detection ---
GPIO.add_event_detect(PIN_CLK, GPIO.FALLING, callback=ausgabeFunktion, bouncetime=100)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=CounterReset, bouncetime=300)


# --- Main loop ---
try:
    while True:
        user_input = input(
            "Press 'L' for previous image, "
            "'A' to change folder, "
            "'R' for next image, or 'Q' to quit: "
        )

        # Quit options
        if user_input.lower() == 'q':
            break
        elif user_input.lower() in ('l', 'r', 'a'):
            break  # Currently all break, could be expanded

        time.sleep(delayTime)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    pass

finally:
    logging.info("quit:")
