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

# Always use this directory
SHARED_BASE_PATH = '/mnt/shared/gta/'

# Create directory if it doesn't exist
os.makedirs(SHARED_BASE_PATH, exist_ok=True)
print(f"Using directory: {SHARED_BASE_PATH}")

# Game and station indices
game_index = 0
station_index = 1  # Start at first station (1), not game logo (0)

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

# GPIO pins for rotary encoder and button
PIN_CLK = 16  # CLK pin (GPIO16)
PIN_DT = 15   # DT pin (GPIO15)  
BUTTON_PIN = 14  # SW pin (GPIO14)

# Setup GPIO
GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Rotary encoder variables
clk_last_state = GPIO.input(PIN_CLK)
button_last_state = GPIO.input(BUTTON_PIN)
last_button_press_time = 0
debounce_delay = 0.02  # 20ms debounce

# Pre-cache data on startup
print("Pre-caching file structure...")
get_radio_stations(force_refresh=True)
display_image(game_index, station_index, force_refresh=True)
print("Cache initialized!")

def get_game_count():
    """Get the number of available games from cache"""
    stations, _ = get_radio_stations()
    return len(stations) if stations else 0

def get_station_count(game_index):
    """Get the number of stations in a game from cache"""
    stations, _ = get_radio_stations()
    if not stations:
        return 0
    
    game_folders = sorted(stations.keys())
    
    if game_index >= len(game_folders):
        return 0
    
    game_name = game_folders[game_index]
    return len(stations[game_name])

def update_display_and_audio(new_station_index):
    """Update display and audio"""
    global station_index
    station_index = new_station_index
    
    # Only update if not in settings mode
    if not settings_manager.in_settings:
        display_image(game_index, station_index)
        play_radio(game_index, station_index - 1)  # -1 because stations start at 0 for radio
        print(f"Game: {game_index}, Station: {station_index}")

def next_station():
    """Move to next station"""
    station_count = get_station_count(game_index)
    if station_count > 0:
        new_station_index = station_index + 1
        if new_station_index > station_count:
            new_station_index = 1  # Wrap around to first station
        update_display_and_audio(new_station_index)
    else:
        print("No stations available")

def previous_station():
    """Move to previous station"""
    station_count = get_station_count(game_index)
    if station_count > 0:
        new_station_index = station_index - 1
        if new_station_index < 1:
            new_station_index = station_count  # Wrap around to last station
        update_display_and_audio(new_station_index)
    else:
        print("No stations available")

def next_game():
    """Move to next game"""
    global game_index, station_index
    game_count = get_game_count()
    if game_count > 0:
        game_index = (game_index + 1) % game_count
        station_index = 1  # Start at first station
        
        # Clear cache when changing games to ensure fresh data
        clear_cache()
        clear_display_cache()
        
        display_image(game_index, station_index)
        play_radio(game_index, station_index - 1)
        print(f"Switched to game: {game_index}")
    else:
        print("No games available")

def previous_game():
    """Move to previous game"""
    global game_index, station_index
    game_count = get_game_count()
    if game_count > 0:
        game_index = (game_index - 1) % game_count
        station_index = 1  # Start at first station
        
        # Clear cache when changing games to ensure fresh data
        clear_cache()
        clear_display_cache()
        
        display_image(game_index, station_index)
        play_radio(game_index, station_index - 1)
        print(f"Switched to game: {game_index}")
    else:
        print("No games available")

def handle_settings_navigation(direction):
    """Handle navigation while in settings mode"""
    if settings_manager.in_playlist_select:
        if direction == 'next':
            settings_manager.next_playlist()
        elif direction == 'previous':
            settings_manager.previous_playlist()
    elif settings_manager.in_settings:
        if direction == 'next':
            settings_manager.next_setting()
        elif direction == 'previous':
            settings_manager.previous_setting()

def handle_space_action():
    """Handle space bar action (same as button press)"""
    result = settings_manager.handle_space()
    
    if result == 'enter_settings':
        print("Entered settings mode - playback stopped")
    elif result == 'enter_playlist_select':
        print("Entered playlist selection")
    elif result == 'brightness_changed':
        print(f"Brightness changed to level {settings_manager.current_brightness_index}")
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
    elif result == 'shutdown':
        print("Shutdown command executed")

def handle_escape_action():
    """Handle escape/back action"""
    result = settings_manager.handle_escape()
    if result == 'back_to_settings':
        print("Back to settings menu")
    elif result == 'exit_settings':
        print("Exited settings mode")

def print_help():
    """Print available commands"""
    print("\n=== GTA Radio Controller ===")
    print("Controls:")
    print("  Rotary Encoder:")
    print("    - Turn LEFT: Previous station/setting")
    print("    - Turn RIGHT: Next station/setting") 
    print("    - Press BUTTON: Enter settings/select")
    print("    - Double-click BUTTON: Switch games")
    print("  Keyboard:")
    print("    [→] or [D]  - Next station/setting")
    print("    [←] or [A]  - Previous station/setting") 
    print("    [↑] or [W]  - Next game")
    print("    [↓] or [S]  - Previous game")
    print("    [SPACE]     - Enter settings/select")
    print("    [ESC]       - Back/exit settings")
    print("    [H]         - Show this help")
    print("    [R]         - Refresh file cache")
    print("    [Q]         - Quit")
    print("    [1-9]       - Jump to station 1-9")
    print("\nSettings Behavior:")
    print("  • Playback STOPS when entering settings")
    print("  • Select playlists without auto-starting playback")
    print("  • Turn encoder to start playback after playlist selection")
    print("  • Press button on brightness to cycle through 5 levels")
    print("  • Press button on Aus.png to shutdown the system")
    print("============================\n")

def get_key():
    """Get a single keypress including arrow keys"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        
        # Check if there's input available
        if select.select([sys.stdin], [], [], 0.1)[0]:
            # Read first character
            ch = sys.stdin.read(1)
            
            # If it's an escape character, check for arrow keys
            if ch == '\x1b':
                # Check if there are more characters available
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch2 = sys.stdin.read(1)
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        ch3 = sys.stdin.read(1)
                        
                        if ch2 == '[':
                            if ch3 == 'A':  # Up arrow
                                return 'UP'
                            elif ch3 == 'B':  # Down arrow
                                return 'DOWN'
                            elif ch3 == 'C':  # Right arrow
                                return 'RIGHT'
                            elif ch3 == 'D':  # Left arrow
                                return 'LEFT'
            
            return ch
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def terminal_control():
    """Handle terminal input in a separate thread"""
    print_help()
    
    while True:
        try:
            key = get_key()
            
            if key is None:
                time.sleep(0.01)
                continue
                
            if key in ['q', 'Q']:
                print("\nShutting down...")
                os._exit(0)
                
            elif key in ['RIGHT', 'd', 'D']:  # Right arrow or D
                if settings_manager.in_settings:
                    handle_settings_navigation('next')
                else:
                    print("Next station")
                    next_station()
                
            elif key in ['LEFT', 'a', 'A']:  # Left arrow or A
                if settings_manager.in_settings:
                    handle_settings_navigation('previous')
                else:
                    print("Previous station")
                    previous_station()
                
            elif key in ['UP', 'w', 'W']:  # Up arrow or W
                if not settings_manager.in_settings:
                    print("Next game")
                    next_game()
                
            elif key in ['DOWN', 's', 'S']:  # Down arrow or S
                if not settings_manager.in_settings:
                    print("Previous game")
                    previous_game()
                
            elif key == ' ':  # SPACE - button press
                handle_space_action()
                
            elif key in ['\x1b', '\x03']:  # ESC or Ctrl+C - back/exit
                handle_escape_action()
                
            elif key in ['h', 'H']:
                print_help()
                
            elif key in ['r', 'R']:
                print("Refreshing cache...")
                clear_cache()
                clear_display_cache()
                get_radio_stations(force_refresh=True)
                print("Cache refreshed!")
                
            elif key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if not settings_manager.in_settings:
                    station_num = int(key)
                    station_count = get_station_count(game_index)
                    if 1 <= station_num <= station_count:
                        update_display_and_audio(station_num)
                    else:
                        print(f"Station {station_num} not available (max: {station_count})")
            else:
                print(f"Unknown key: {repr(key)}")
                    
        except Exception as e:
            print(f"Error in terminal control: {e}")

def read_rotary_encoder():
    """Read rotary encoder state and handle rotation"""
    global clk_last_state
    
    clk_state = GPIO.input(PIN_CLK)
    dt_state = GPIO.input(PIN_DT)
    
    # Check for rotation
    if clk_state != clk_last_state:
        # CLK pin changed state, so rotation occurred
        if dt_state != clk_state:
            # Turning clockwise (right)
            if settings_manager.in_settings:
                handle_settings_navigation('next')
            else:
                next_station()
        else:
            # Turning counter-clockwise (left)
            if settings_manager.in_settings:
                handle_settings_navigation('previous')
            else:
                previous_station()
        
        clk_last_state = clk_state
        time.sleep(debounce_delay)  # Debounce

def read_button():
    """Read button state and handle presses"""
    global button_last_state, last_button_press_time
    
    button_state = GPIO.input(BUTTON_PIN)
    current_time = time.time()
    
    # Check for button press (active low - button pressed when LOW)
    if button_state == GPIO.LOW and button_last_state == GPIO.HIGH:
        # Button just pressed
        if current_time - last_button_press_time < 0.5:  # Double click within 500ms
            # Double click - switch game
            if not settings_manager.in_settings:
                next_game()
        else:
            # Single click - handle as space action
            handle_space_action()
        
        last_button_press_time = current_time
        time.sleep(debounce_delay)  # Debounce
    
    button_last_state = button_state

def rotary_control():
    """Handle rotary encoder input in a separate thread"""
    print("Rotary encoder control started")
    
    while True:
        try:
            read_rotary_encoder()
            read_button()
            time.sleep(0.001)  # Small delay to prevent CPU overload
        except Exception as e:
            print(f"Error in rotary control: {e}")
            time.sleep(0.1)

# Start control threads
print("Starting control threads...")
terminal_thread = threading.Thread(target=terminal_control, daemon=True)
terminal_thread.start()

rotary_thread = threading.Thread(target=rotary_control, daemon=True)
rotary_thread.start()

print("Radio system started!")
print("Rotary encoder: ENABLED")
print("  - Turn: Navigate stations/settings")
print("  - Press: Enter settings/select")
print("  - Double-click: Switch games")
print("Keyboard controls also available - Press 'H' for help")

# Initial playback
if get_station_count(game_index) > 0:
    play_radio(game_index, station_index - 1)

try:
    while True:
        # Keep the main thread alive and print status occasionally
        time.sleep(5)
        
        # Print status every 30 seconds
        if int(time.time()) % 30 == 0:
            stations, _ = get_radio_stations()
            if stations:
                game_folders = sorted(stations.keys())
                current_game = game_folders[game_index] if game_index < len(game_folders) else "Unknown"
                station_count = get_station_count(game_index)
                mode = "SETTINGS" if settings_manager.in_settings else "RADIO"
                print(f"Status: {mode} | Game: '{current_game}' | Station: {station_index}/{station_count}")

except KeyboardInterrupt:
    print("\nShutting down...")
except Exception as e:
    print(f"Error in main loop: {e}")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up")