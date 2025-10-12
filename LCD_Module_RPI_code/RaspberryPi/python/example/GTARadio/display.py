#!/usr/bin/python
# -*- coding: UTF-8 -*- import chardet
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import LCD_1inch28
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from evdev import UInput, ecodes as e
import subprocess

from radio import play_radio
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



# Function to get a list of image files in the specified folder
def get_image_files(folder):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(tuple(image_extensions))]
    return image_files



current_image_index = 0
current_folder_index = 0

disp = LCD_1inch28.LCD_1inch28()
disp.Init()
disp.clear()


def display_image(folder_index, image_index):
#GTA3
    if folder_index == 0:
        if image_index == 0:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/GameLogos/GTA3.png')
        if image_index == 1:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/CHAT.png')
        if image_index == 2:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/CLASS.png')
        if image_index == 3:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/FLASH.png')
        if image_index == 4:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/GAME.png')
        if image_index == 5:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/HEAD.png')
        if image_index == 6:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/KJAH.png')
        if image_index == 7:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/LIPS.png')
        if image_index == 8:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/MSX.png')
        if image_index == 9:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA3/RISE.png')
#GTAVC
    elif folder_index == 1:
        if image_index == 0:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/GameLogos/GTAVC.png')
        if image_index == 1:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/EMOTION.png')
        if image_index == 2:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/ESPANT.png')
        if image_index == 3:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/FEVER.png')
        if image_index == 4:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/FLASH.png')
        if image_index == 5:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/KCHAT.png')
        if image_index == 6:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/VCPR.png')
        if image_index == 7:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/VROCK.png')
        if image_index == 8:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/WAVE.png')
        if image_index == 9:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTAVC/WILD.png')
#GTASA
    elif folder_index == 2:
        if image_index == 0:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/GameLogos/GTASA.png')
        if image_index == 1:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/Bounce FM.png')
        elif image_index == 2:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/CSR 103.9.png')
        elif image_index == 3:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/K-DST.png')
        elif image_index == 4:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/K-JAH West.png')
        elif image_index == 5:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/K-Rose.png')
        elif image_index == 6:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/Master Sounds 98.3.png')
        elif image_index == 7:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/Playback FM.png')
        elif image_index == 8:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/Radio Los Santos.png')
        elif image_index == 9:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/Radio X.png')
        elif image_index == 10:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/SF-UR.png')
        elif image_index == 11:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTASA/West Coast Talk Radio.png')
#GTA4
    elif folder_index == 3:
        if image_index == 0:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/GameLogos/GTA4.png')
        if image_index == 1:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Electro-Choc.png')
        elif image_index == 2:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Integrity 2.0.png')
        elif image_index == 3:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Jazz Nation Radio 108.5.png')
        elif image_index == 4:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/K109 The Studio.png')
        elif image_index == 5:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Liberty City Hardcore.png')
        elif image_index == 6:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Liberty Rock Radio.png')
        elif image_index == 7:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Massive B Soundsystem 96.9.png')
        elif image_index == 8:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Public Liberty Radio.png')
        elif image_index == 9:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Radio Broker.png')
        elif image_index == 10:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/RamJam FM.png')
        elif image_index == 11:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/San Juan Sounds.png')
        elif image_index == 12:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Self-Actualization FM.png')
        elif image_index == 13:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/The Beat 102.7.png')
        elif image_index == 14:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/The Classics 104.1.png')
        elif image_index == 15:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/The Journey.png')
        elif image_index == 16:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/The Vibe 98.8.png')
        elif image_index == 17:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Tuff Gong Radio.png')
        elif image_index == 18:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Vice City FM.png')
        elif image_index == 19:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/Vladivostok FM.png')
        elif image_index == 20:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA4/WKTT Radio.png')
#GTA5
    elif folder_index == 4:
        if image_index == 0:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/GameLogos/GTA5.png')
        if image_index == 1:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/BlaineCountyRadio.png')
        elif image_index == 2:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/blondedLosSantos97.8FM.png')
        elif image_index == 3:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/ChannelX.png')
        elif image_index == 4:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/EastLosFM.png')
        elif image_index == 5:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/FlyLoFM.png')
        elif image_index == 6:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/LosSantosRockRadio.png')
        elif image_index == 7:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/Non-Stop-PopFM.png')
        elif image_index == 8:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/RadioMirrorPark.png')
        elif image_index == 9:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/RebelRadio.png')
        elif image_index == 10:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/Space103.2.png')
        elif image_index == 11:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/SoulwaxFM.png')
        elif image_index == 12:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/TheBlueArk.png')
        elif image_index == 13:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/TheLab.png')
        elif image_index == 14:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/TheLowdown91.1.png')
        elif image_index == 15:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/VinewoodBoulevardRadio.png')
        elif image_index == 16:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/WCTR.png')
        elif image_index == 17:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/WestCoastClassics.png')
        elif image_index == 18:
            image = Image.open('/home/viktor/LCD_Module_RPI_code/RaspberryPi/python/RadioLogos/GTA5/WorldWideFM.png')

    im_r = image.rotate(0)
    disp.ShowImage(im_r)


def display_image_delay(folder_index, image_index):
    time.sleep(2)
    display_image(folder_index,image_index)
    play_radio(folder_index, image_index)
