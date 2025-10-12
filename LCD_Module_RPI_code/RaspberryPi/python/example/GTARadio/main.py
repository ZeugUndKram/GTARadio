import os
import sys
import time
import logging
import spidev as SPI
import RPi.GPIO as GPIO
import threading
import select
import termios
import tty
import sys

GPIO.setmode(GPIO.BCM)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont

from display import display_image, display_image_delay, clear_display_cache
from radio import play_radio, get_radio_stations, clear_cache
from settings import settings_manager

# ... (existing configuration code remains the same) ...

def update_display_and_audio(new_station_index):
    """Update display and audio"""
    global station_index
    station_index = new_station_index
    
    # Only update if not in settings mode
    if not settings_manager.in_settings:
        display_image(game_index, station_index)
        play_radio(game_index, station_index - 1)
        print(f"Game: {game_index}, Station: {station_index}")

def handle_space_action():
    """Handle space bar action"""
    result = settings_manager.handle_space()
    
    if result == 'enter_settings':
        print("Entered settings mode - playback stopped")
    elif result == 'enter_playlist_select':
        print("Entered playlist selection")
    elif isinstance(result, tuple) and result[0] == 'select_playlist':
        global game_index, station_index
        game_index = result[1]
        station_index = 1  # Set to first station but DON'T start playback
        
        # Clear cache and update display only
        clear_cache()
        clear_display_cache()
        display_image(game_index, station_index)
        
        # Don't start playback - user needs to manually select a station
        stations, _ = get_radio_stations()
        if stations:
            game_folders = sorted(stations.keys())
            game_name = game_folders[game_index] if game_index < len(game_folders) else "Unknown"
            print(f"Switched to playlist: {game_name} (ready - turn encoder to start playback)")

def handle_escape_action():
    """Handle escape/back action"""
    result = settings_manager.handle_escape()
    if result == 'back_to_settings':
        print("Back to settings menu")
    elif result == 'exit_settings':
        print("Exited settings mode")
        # Note: Playback remains stopped until user selects a station

# ... (rest of the main.py remains the same as previous version) ...