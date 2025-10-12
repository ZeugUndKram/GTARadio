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

SHARED_BASE_PATH = '/mnt/shared/'

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

def get_image_path(game_index, station_index):
    """Get the path to the appropriate image based on game and station"""
    if not os.path.exists(SHARED_BASE_PATH):
        return None
    
    game_folders = sorted([f for f in os.listdir(SHARED_BASE_PATH) 
                          if os.path.isdir(os.path.join(SHARED_BASE_PATH, f))])
    
    if game_index >= len(game_folders):
        return None
    
    game_name = game_folders[game_index]
    game_path = os.path.join(SHARED_BASE_PATH, game_name)
    
    # If station_index is 0, look for game logo
    if station_index == 0:
        # Look for common game logo names
        game_logo_names = ['game.png', 'game.jpg', 'logo.png', 'logo.jpg', game_name + '.png', game_name + '.jpg']
        for logo_name in game_logo_names:
            logo_path = os.path.join(game_path, logo_name)
            if os.path.exists(logo_path):
                return logo_path
        return None
    
    # For stations, get the station name from MP3 files
    mp3_files = sorted([f for f in os.listdir(game_path) if f.lower().endswith('.mp3')])
    
    if station_index - 1 >= len(mp3_files):
        return None
    
    mp3_file = mp3_files[station_index - 1]
    station_name = os.path.splitext(mp3_file)[0]
    
    # Look for image with same name as MP3
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    for ext in image_extensions:
        image_path = os.path.join(game_path, station_name + ext)
        if os.path.exists(image_path):
            return image_path
    
    return None

def display_image(game_index, station_index):
    image_path = get_image_path(game_index, station_index)
    
    if image_path and os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            im_r = image.rotate(0)
            disp.ShowImage(im_r)
            print(f"Displayed: {image_path}")
        except Exception as e:
            print(f"Error displaying image {image_path}: {e}")
            # Display default/error image
            show_default_image()
    else:
        print(f"Image not found for game {game_index}, station {station_index}")
        show_default_image()

def show_default_image():
    """Display a default image when no specific image is found"""
    try:
        # Create a simple default image
        image = Image.new('RGB', (240, 240), color='black')
        draw = ImageDraw.Draw(image)
        # You can add text or a simple graphic here
        im_r = image.rotate(0)
        disp.ShowImage(im_r)
    except Exception as e:
        print(f"Error showing default image: {e}")

def display_image_delay(game_index, station_index):
    time.sleep(2)
    display_image(game_index, station_index)