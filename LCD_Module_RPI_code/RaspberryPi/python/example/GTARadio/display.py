#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import tempfile
from mutagen import File
from mutagen.id3 import ID3, APIC

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
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

# Brightness levels (0-4) mapped to brightness factors
BRIGHTNESS_FACTORS = [0.3, 0.5, 0.7, 0.85, 1.0]  # hell_0 to hell_4

def get_current_brightness_factor():
    """Get the current brightness factor from settings"""
    try:
        from settings import settings_manager
        brightness_index = settings_manager.current_brightness_index
        return BRIGHTNESS_FACTORS[brightness_index]
    except:
        return 1.0  # Default full brightness

def apply_brightness(image, brightness_factor):
    """Apply brightness adjustment to an image"""
    try:
        if brightness_factor < 1.0:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply brightness using ImageEnhance
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness_factor)
            
            # Also reduce contrast for more natural dimming
            if brightness_factor < 0.7:
                contrast_enhancer = ImageEnhance.Contrast(image)
                image = contrast_enhancer.enhance(0.9)
        
        return image
    except Exception as e:
        print(f"Error applying brightness: {e}")
        return image

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

def extract_mp3_cover(mp3_path, station_name, game_path):
    """Extract embedded cover art from MP3 file and save as image"""
    try:
        audio = File(mp3_path, easy=True)
        if audio is None:
            return None
        
        cover_data = None
        mime_type = 'image/jpeg'  # default
        
        # Method 1: ID3v2 APIC frames
        try:
            id3 = ID3(mp3_path)
            pictures = [tag for tag in id3.values() if isinstance(tag, APIC)]
            if pictures:
                cover_data = pictures[0].data
                mime_type = pictures[0].mime
                print(f"Found ID3v2 cover art in {mp3_path}")
        except Exception as e:
            pass
        
        # Method 2: Check common tags in easyid3
        if not cover_data and hasattr(audio, 'tags'):
            cover_tags = [
                'APIC:', 'cover', 'coverart', 'albumart', 
                'metadata_block_picture', 'PICTURE', 'PIC'
            ]
            for tag_name in cover_tags:
                if tag_name in audio.tags:
                    if hasattr(audio.tags[tag_name], 'data'):
                        cover_data = audio.tags[tag_name].data
                    else:
                        cover_data = audio.tags[tag_name][0]
                    print(f"Found cover art in tag {tag_name} in {mp3_path}")
                    break
        
        # Method 3: Check for embedded images in any tag
        if not cover_data and hasattr(audio, 'tags'):
            for tag in audio.tags.values():
                if hasattr(tag, 'data') and len(tag.data) > 100:  # Reasonable image size
                    # Check if it looks like image data
                    if tag.data.startswith((b'\xff\xd8\xff', b'\x89PNG', b'GIF', b'BM')):
                        cover_data = tag.data
                        print(f"Found image data in tag in {mp3_path}")
                        break
        
        if cover_data:
            # Determine file extension from MIME type or data
            extension = '.jpg'
            if 'png' in mime_type.lower() or cover_data.startswith(b'\x89PNG'):
                extension = '.png'
            elif 'gif' in mime_type.lower() or cover_data.startswith(b'GIF'):
                extension = '.gif'
            elif 'bmp' in mime_type.lower() or cover_data.startswith(b'BM'):
                extension = '.bmp'
            
            # Save extracted cover
            cover_path = os.path.join(game_path, f"{station_name}_mp3cover{extension}")
            
            with open(cover_path, 'wb') as f:
                f.write(cover_data)
            
            print(f"Extracted cover art: {cover_path}")
            return cover_path
        
        print(f"No cover art found in {mp3_path}")
        return None
        
    except Exception as e:
        print(f"Error extracting cover art from {mp3_path}: {e}")
        return None

def get_mp3_cover_path(game_index, display_index):
    """Get cover art path from MP3 file"""
    games = get_available_games()
    if game_index >= len(games):
        return None
    
    game_name = games[game_index]
    game_path = os.path.join(SHARED_BASE_PATH, game_name)
    
    station_files = get_station_files(game_index)
    station_index = display_index - 1
    
    if station_index < len(station_files):
        mp3_file = station_files[station_index]
        station_name = os.path.splitext(mp3_file)[0]
        mp3_path = os.path.join(game_path, mp3_file)
        
        if os.path.exists(mp3_path):
            # First check if we already extracted this cover
            existing_covers = [
                f for f in os.listdir(game_path) 
                if f.startswith(f"{station_name}_mp3cover") or f.startswith(f"{station_name}_cover")
            ]
            if existing_covers:
                return os.path.join(game_path, existing_covers[0])
            
            # Extract fresh cover art
            return extract_mp3_cover(mp3_path, station_name, game_path)
    
    return None

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

def get_image_path_with_priority(game_index, display_index, force_refresh=False):
    """
    Get image path with priority:
    1. Dedicated image file (PNG, JPG, etc.)
    2. Embedded MP3 cover art
    3. Default generated image
    """
    # Priority 1: Dedicated image file
    image_path = get_image_path(game_index, display_index, force_refresh)
    if image_path and os.path.exists(image_path):
        return image_path
    
    # Priority 2: MP3 cover art (only for stations, not game logos)
    if display_index > 0:
        mp3_cover_path = get_mp3_cover_path(game_index, display_index)
        if mp3_cover_path:
            return mp3_cover_path
    
    # Priority 3: Default generated image (already handled in get_image_path)
    return image_path

def display_settings_image(setting_index):
    """Display settings images"""
    # These are just the base names - the actual brightness image will be dynamic
    settings_base_images = [
        'playlist.png',
        'hell_0.png',  # This gets replaced with current brightness level
        'Aus.png'
    ]
    
    if setting_index < len(settings_base_images):
        # For brightness setting, we need to get the current level from settings_manager
        if setting_index == 1:  # brightness setting
            from settings import settings_manager
            current_brightness_image = f"hell_{settings_manager.current_brightness_index}.png"
            image_path = os.path.join(os.path.dirname(__file__), 'assets', current_brightness_image)
        else:
            image_path = os.path.join(os.path.dirname(__file__), 'assets', settings_base_images[setting_index])
        
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                if image.size != (240, 240):
                    image = image.resize((240, 240), Image.Resampling.LANCZOS)
                
                # Apply current brightness to settings images too
                brightness_factor = get_current_brightness_factor()
                image = apply_brightness(image, brightness_factor)
                
                im_r = image.rotate(0)
                disp.ShowImage(im_r)
                print(f"Displayed settings image: {os.path.basename(image_path)} (brightness: {brightness_factor})")
            except Exception as e:
                print(f"Error displaying settings image: {e}")
                show_default_image()
        else:
            print(f"Settings image not found: {image_path}")
            show_default_image()
    else:
        show_default_image()

def display_shutdown_image():
    """Display the Shutdown.png image"""
    shutdown_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'Shutdown.png')
    if os.path.exists(shutdown_image_path):
        try:
            image = Image.open(shutdown_image_path)
            if image.size != (240, 240):
                image = image.resize((240, 240), Image.Resampling.LANCZOS)
            
            # Don't apply brightness to shutdown image - keep it full brightness
            im_r = image.rotate(0)
            disp.ShowImage(im_r)
            print("Displayed Shutdown.png")
        except Exception as e:
            print(f"Error displaying shutdown image: {e}")
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
        
        # Apply brightness to generated image
        brightness_factor = get_current_brightness_factor()
        image = apply_brightness(image, brightness_factor)
        
        im_r = image.rotate(0)
        disp.ShowImage(im_r)
    except Exception as e:
        print(f"Error displaying playlist name: {e}")
        show_default_image()

def display_image(game_index, display_index, force_refresh=False):
    """Display image with support for settings mode and MP3 cover art fallback"""
    if game_index == -1:
        # Settings mode
        display_settings_image(display_index)
        return
    elif game_index == -2:
        # Shutdown screen
        display_shutdown_image()
        return
    
    # Normal game/station display with MP3 cover art fallback
    image_path = get_image_path_with_priority(game_index, display_index, force_refresh)
    
    if image_path and os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            # Resize image to fit display if needed
            if image.size != (240, 240):
                image = image.resize((240, 240), Image.Resampling.LANCZOS)
            
            # Apply current brightness setting
            brightness_factor = get_current_brightness_factor()
            image = apply_brightness(image, brightness_factor)
            
            im_r = image.rotate(0)
            
            # Cache the image
            cache_key = f"{game_index}_{display_index}"
            _image_cache[cache_key] = im_r
            
            disp.ShowImage(im_r)
            print(f"Displayed image with brightness: {brightness_factor}")
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
        
        # Apply brightness to default image too
        brightness_factor = get_current_brightness_factor()
        image = apply_brightness(image, brightness_factor)
        
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