import os
import sys
import time
import logging
import spidev as SPI
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont
from evdev import UInput, ecodes as e
import subprocess
import threading

from display import display_image, display_image_delay
from radio import play_radio, get_radio_stations

SHARED_BASE_PATH = '/mnt/shared/'

# Game and station indices
game_index = 0
station_index = 0  # 0 = game logo, 1+ = stations

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

GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Rotary encoder variables
Counter = 0
Richtung = True
PIN_CLK_LETZTER = 0
PIN_CLK_AKTUELL = 0
delayTime = 0.02

# Initial pin state
PIN_CLK_LETZTER = GPIO.input(PIN_CLK)

last_reset_time = 0
reset_pressed = False

def get_game_count():
    """Get the number of available games"""
    if not os.path.exists(SHARED_BASE_PATH):
        return 0
    return len([f for f in os.listdir(SHARED_BASE_PATH) 
                if os.path.isdir(os.path.join(SHARED_BASE_PATH, f))])

def get_station_count(game_index):
    """Get the number of stations in a game"""
    stations, _ = get_radio_stations()
    if not stations:
        return 1  # At least show game logo
    
    game_folders = sorted(stations.keys())
    
    if game_index >= len(game_folders):
        return 1
    
    game_name = game_folders[game_index]
    return len(stations[game_name]) + 1  # +1 for game logo

# Initial display (show game logo)
display_image(game_index, station_index)

def ausgabeFunktion(null):
    global station_index, game_index
    
    PIN_CLK_AKTUELL = GPIO.input(PIN_CLK)

    if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:
        station_count = get_station_count(game_index)
        
        if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
            # Turning right
            station_index += 1
            if station_index >= station_count:
                station_index = 0
            display_image(game_index, station_index)
            if station_index > 0:  # Only play if it's a station (not game logo)
                play_radio(game_index, station_index - 1)  # -1 because stations start at 0 for radio
            print(f"Game: {game_index}, Station: {station_index}")
            Richtung = True
        else:
            # Turning left
            station_index -= 1
            if station_index < 0:
                station_index = station_count - 1
            display_image(game_index, station_index)
            if station_index > 0:  # Only play if it's a station (not game logo)
                play_radio(game_index, station_index - 1)  # -1 because stations start at 0 for radio
            Richtung = False
            print(f"Game: {game_index}, Station: {station_index}")

def CounterReset(null):
    global last_reset_time, game_index, station_index
    
    current_time = time.time()
    if current_time - last_reset_time < 2:
        # Double click - change game
        game_count = get_game_count()
        if game_count > 0:
            game_index = (game_index + 1) % game_count
            station_index = 0  # Show game logo when switching games
            display_image(game_index, station_index)
            print(f"Switched to game: {game_index}")
    
    last_reset_time = current_time
    print("Button pressed")

# Setup interrupts
GPIO.add_event_detect(PIN_CLK, GPIO.FALLING, callback=ausgabeFunktion, bouncetime=100)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=CounterReset, bouncetime=300)

print("Radio system started!")
print("Rotate encoder to browse stations, double-click button to switch games")

try:
    while True:
        # Just keep the main thread alive
        time.sleep(1)

except IOError as e:
    logging.error(e)
except KeyboardInterrupt:
    pass
finally:
    logging.info("Shutting down...")
    GPIO.cleanup()