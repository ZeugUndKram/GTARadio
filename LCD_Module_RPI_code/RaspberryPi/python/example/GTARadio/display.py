#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

SHARED_BASE_PATH = '/mnt/shared/gta/'

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

disp = LCD_1inch28.LCD_1inch28()
disp.Init()
disp.clear()

# Cache variables
_games_cache = None
_station_files_cache = {}
_image_cache = {}  # Cache for loaded images
_last_cache_update = 0
CACHE_TIMEOUT = 30  # seconds

def get_available_games(force_refresh=False):
    """Get list of available games with caching"""
    global _games_cache, _last_cache_update
    
    current_time = time.time()
    
    if not force_refresh and _games_cache is not None and current_time - _last_cache_update < CACHE_TIMEOUT:
        return _games_cache
    
    if not os.path.exists(SHARED_BASE_PATH):
        _games_cache = []
        return _games_cache
    
    games = sorted([f for f in os.listdir(SHARED_BASE_PATH) 
                   if os.path.isdir(os.path.join(SHARED_BASE_PATH, f))])
    
    _games_cache = games
    _last_cache_update = current_time
    return games

def get_station_files(game_index, force_refresh=False):
    """Get MP3 files for a game with caching"""
    global _station_files_cache
    
    games = get_available_games(force_refresh)
    if game_index >= len(games):
        return []
    
    game_name = games[game_index]
    
    # Return cached data if available
    if not force_refresh and game_name in _station_files_cache:
        return _station_files_cache[game_name]
    
    game_path = os.path.join(SHARED_BASE_PATH, game_name)
    
    try:
        mp3_files = sorted([f for f in os.listdir(game_path) if f.lower().endswith('.mp3')])
    except PermissionError:
        print(f"Permission denied accessing: {game_path}")
        mp3_files = []
    
    _station_files_cache[game_name] = mp3_files
    return mp3_files

def get_image_path(game_index, display_index, force_refresh=False):
    """Get the path to the appropriate image based on game and station with caching"""
    games = get_available_games(force_refresh)
    if game_index >= len(games):
        return None
    
    game_name = games[game_index]
    game_path = os.path.join(SHARED_BASE_PATH, game_name)
    
    # If display_index is 0, show game logo
    if display_index == 0:
        # Look for common game logo names
        game_logo_names = ['game.png', 'game.jpg', 'logo.png', 'logo.jpg', 
                          f'{game_name}.png', f'{game_name}.jpg',
                          'cover.png', 'cover.jpg', 'default.png']
        for logo_name in game_logo_names:
            logo_path = os.path.join(game_path, logo_name)
            if os.path.exists(logo_path):
                return logo_path
        # If no game logo found, create a default one
        return create_default_game_image(game_name, game_path)
    
    # For stations (display_index >= 1), get the station image
    station_files = get_station_files(game_index, force_refresh)
    station_index = display_index - 1  # Convert to 0-based station index
    
    if station_index >= len(station_files):
        return None
    
    mp3_file = station_files[station_index]
    station_name = os.path.splitext(mp3_file)[0]
    
    # Look for image with same name as MP3
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    for ext in image_extensions:
        image_path = os.path.join(game_path, station_name + ext)
        if os.path.exists(image_path):
            return image_path
    
    # Also check for images without spaces/special characters
    simple_name = station_name.replace(' ', '').replace('-', '').lower()
    for ext in image_extensions:
        try:
            for file in os.listdir(game_path):
                if (file.lower().startswith(simple_name) and 
                    file.lower().endswith(ext) and
                    not file.lower().endswith('.mp3')):
                    image_path = os.path.join(game_path, file)
                    return image_path
        except PermissionError:
            continue
    
    # If no station image found, create a default one
    return create_default_station_image(station_name, game_path)

def display_settings_image(setting_index):
    """Display settings images"""
    settings_images = [
        'playlist.png'
    ]
    
    if setting_index < len(settings_images):
        image_path = os.path.join(os.path.dirname(__file__), 'assets', settings_images[setting_index])
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                if image.size != (240, 240):
                    image = image.resize((240, 240), Image.Resampling.LANCZOS)
                im_r = image.rotate(0)
                disp.ShowImage(im_r)
                print(f"Displayed settings: {settings_images[setting_index]}")
            except Exception as e:
                print(f"Error displaying settings image: {e}")
                show_default_image()
        else:
            show_default_image()
    else:
        show_default_image()

def display_playlist_name(playlist_name):
    """Display playlist name when no logo exists"""
    try:
        image = Image.new('RGB', (240, 240), color='darkblue')
        draw = ImageDraw.Draw(image)
        
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Display "SELECT PLAYLIST" at top
        draw.text((120, 50), "SELECT PLAYLIST", fill='yellow', font=font_small, anchor="mm")
        
        # Split playlist name if too long
        words = playlist_name.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) < 15:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw playlist name lines
        y_pos = 120 - (len(lines) * 15)
        for line in lines:
            draw.text((120, y_pos), line, fill='white', font=font_large, anchor="mm")
            y_pos += 30
        
        im_r = image.rotate(0)
        disp.ShowImage(im_r)
    except Exception as e:
        print(f"Error displaying playlist name: {e}")
        show_default_image()

def display_image(game_index, display_index, force_refresh=False):
    """Display image with support for settings mode"""
    if game_index == -1:
        # Settings mode
        display_settings_image(display_index)
        return
    
    # Normal game/station display
    image_path = get_image_path(game_index, display_index, force_refresh)
    
    if image_path and os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            # Resize image to fit display if needed
            if image.size != (240, 240):
                image = image.resize((240, 240), Image.Resampling.LANCZOS)
            im_r = image.rotate(0)
            
            # Cache the image
            cache_key = f"{game_index}_{display_index}"
            _image_cache[cache_key] = im_r
            
            disp.ShowImage(im_r)
        except Exception as e:
            print(f"Error displaying image {image_path}: {e}")
            # If it's a game logo that failed, show playlist name instead
            if display_index == 0:
                games = get_available_games()
                if game_index < len(games):
                    display_playlist_name(games[game_index])
            else:
                show_default_image()
    else:
        # If no image found and it's a game logo, show playlist name
        if display_index == 0:
            games = get_available_games()
            if game_index < len(games):
                display_playlist_name(games[game_index])
            else:
                show_default_image()
        else:
            show_default_image()

def show_default_image():
    """Display a default image when no specific image is found"""
    try:
        image = Image.new('RGB', (240, 240), color='black')
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font = ImageFont.load_default()
        draw.text((120, 120), "NO IMAGE", fill='white', font=font, anchor="mm")
        im_r = image.rotate(0)
        disp.ShowImage(im_r)
    except Exception as e:
        print(f"Error showing default image: {e}")

def clear_display_cache():
    """Clear the display cache"""
    global _games_cache, _station_files_cache, _image_cache, _last_cache_update
    _games_cache = None
    _station_files_cache = {}
    _image_cache = {}
    _last_cache_update = 0
    print("Display cache cleared")

def display_image_delay(game_index, station_index):
    time.sleep(0.1)  # Reduced delay
    display_image(game_index, station_index)

# Default image creation functions
def create_default_game_image(game_name, game_path):
    """Create a default game logo image"""
    try:
        image = Image.new('RGB', (240, 240), color='navy')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((120, 100), game_name, fill='white', font=font, anchor="mm")
        draw.text((120, 130), "RADIO", fill='yellow', font=font, anchor="mm")
        
        default_path = os.path.join(game_path, "default_game.png")
        image.save(default_path)
        return default_path
    except Exception as e:
        print(f"Error creating default game image: {e}")
        return None

def create_default_station_image(station_name, game_path):
    """Create a default station image"""
    try:
        image = Image.new('RGB', (240, 240), color='darkgreen')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Split long station names
        words = station_name.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) < 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw text lines
        y_pos = 100 - (len(lines) * 12)
        for line in lines:
            draw.text((120, y_pos), line, fill='white', font=font, anchor="mm")
            y_pos += 24
        
        default_path = os.path.join(game_path, f"{station_name}.png")
        image.save(default_path)
        return default_path
    except Exception as e:
        print(f"Error creating default station image: {e}")
        return None