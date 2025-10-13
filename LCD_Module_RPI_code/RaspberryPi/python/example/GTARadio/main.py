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
from radio import start_playback_monitor

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

# Only setup GPIO if rotary encoder is connected
try:
    PIN_CLK = 16
    PIN_DT = 15
    BUTTON_PIN = 14

    GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    ROTARY_ENCODER_AVAILABLE = True
    print("Rotary encoder initialized")
except Exception as e:
    print(f"Rotary encoder not available: {e}")
    ROTARY_ENCODER_AVAILABLE = False

# Rotary encoder variables
if ROTARY_ENCODER_AVAILABLE:
    PIN_CLK_LETZTER = GPIO.input(PIN_CLK)
last_reset_time = 0

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

def print_help():
    """Print available commands"""
    print("\n=== GTA Radio Controller ===")
    print("Keyboard Controls:")
    print("  [→] or [D]  - Next station/setting")
    print("  [←] or [A]  - Previous station/setting") 
    print("  [↑] or [W]  - Next game")
    print("  [↓] or [S]  - Previous game")
    print("  [SPACE]     - Enter settings/select/shutdown/change brightness")
    print("  [ESC]       - Back/exit settings")
    print("  [H]         - Show this help")
    print("  [R]         - Refresh file cache")
    print("  [Q]         - Quit")
    print("  [1-9]       - Jump to station 1-9")
    print("\nSettings Behavior:")
    print("  • Playback STOPS when entering settings")
    print("  • Select playlists without auto-starting playback")
    print("  • Turn encoder to start playback after playlist selection")
    print("  • Press SPACE on brightness to cycle through 5 levels")
    print("  • Press SPACE on Aus.png to shutdown the system")
    print("============================\n")

def get_key():
    """Get a single keypress including arrow keys"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        
        # Read first character
        ch = sys.stdin.read(1)
        
        # If it's an escape character, check for arrow keys
        if ch == '\x1b':
            # Read the next two characters
            ch2 = sys.stdin.read(1)
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
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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
    """Handle space bar action"""
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
        # The system will shut down automatically
        # We don't need to do anything else here

def handle_escape_action():
    """Handle escape/back action"""
    result = settings_manager.handle_escape()
    if result == 'back_to_settings':
        print("Back to settings menu")
    elif result == 'exit_settings':
        print("Exited settings mode")
        # Note: Playback remains stopped until user selects a station

def handle_space_action():
    """Handle space bar action"""
    result = settings_manager.handle_space()
    
    if result == 'enter_settings':
        print("Entered settings mode - playback stopped")
    elif result == 'enter_playlist_select':
        print("Entered playlist selection")
    elif result == 'brightness_changed':
        print(f"Brightness changed to level {settings_manager.current_brightness_index}")
    elif result == 'playback_mode_changed':
        print(f"Playback mode changed to: {settings_manager.current_playback_mode}")
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
        # The system will shut down automatically
        # We don't need to do anything else here"

def terminal_control():
    """Handle terminal input in a separate thread"""
    print_help()
    
    while True:
        try:
            key = get_key()
            
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
                
            elif key == ' ':  # SPACE - rotary encoder press
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

# Rotary encoder functions (only if available)
if ROTARY_ENCODER_AVAILABLE:
    def ausgabeFunktion(null):
        global PIN_CLK_LETZTER
        
        PIN_CLK_AKTUELL = GPIO.input(PIN_CLK)

        if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:
            if settings_manager.in_settings:
                # In settings mode - navigate settings
                if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                    handle_settings_navigation('next')
                else:
                    handle_settings_navigation('previous')
            else:
                # Normal mode - navigate stations
                if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
                    next_station()
                else:
                    previous_station()
            
        PIN_CLK_LETZTER = PIN_CLK_AKTUELL

    def CounterReset(null):
        # Now space bar handles this in terminal_control
        pass

    # Setup interrupts
    GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=ausgabeFunktion, bouncetime=200)
    # Note: Button press is now handled by space bar in terminal

# Start terminal control in a separate thread
terminal_thread = threading.Thread(target=terminal_control, daemon=True)
terminal_thread.start()
start_playback_monitor()

print("Radio system started!")
if ROTARY_ENCODER_AVAILABLE:
    print("Rotary encoder: ENABLED")
    print("Rotate encoder to browse stations, double-click button to switch games")
else:
    print("Rotary encoder: DISABLED (using keyboard controls only)")
print("Press 'H' for help with keyboard controls")

# Initial playback
if get_station_count(game_index) > 0:
    play_radio(game_index, station_index - 1)

try:
    while True:
        # Keep the main thread alive
        time.sleep(1)
        
        # Optional: Print status every 30 seconds
        if int(time.time()) % 30 == 0:
            stations, _ = get_radio_stations()
            if stations:
                game_folders = sorted(stations.keys())
                current_game = game_folders[game_index] if game_index < len(game_folders) else "Unknown"
                print(f"Status: Game '{current_game}', Station {station_index}")

except KeyboardInterrupt:
    print("\nShutting down...")
except Exception as e:
    print(f"Error in main loop: {e}")
finally:
    if ROTARY_ENCODER_AVAILABLE:
        GPIO.cleanup()