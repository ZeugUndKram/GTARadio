#!/usr/bin/env python3
"""
Test script for input.py with pre-configured pins
"""

import input
import time
import signal
import sys

def rotation_handler(direction, counter):
    if direction == 1:
        print(f"↻ CLOCKWISE - Position: {counter}")
    else:
        print(f"↺ COUNTER-CLOCKWISE - Position: {counter}")

def button_handler():
    print("🔘 BUTTON PRESSED!")

# Initialize encoder with DEFAULT pins (14, 15, 16)
encoder = input.init_encoder()

# Set up handlers
encoder.on_rotate(rotation_handler)
encoder.on_button_press(button_handler)

print("Rotary encoder ready with pins 14, 15, 16!")
print("Wiring:")
print("CLK → GPIO14 (physical pin 8)")
print("DT  → GPIO15 (physical pin 10)")
print("SW  → GPIO16 (physical pin 36)")
print("+   → 3.3V   (pin 1)")
print("GND → Ground (pin 6)")
print("\nTurn the knob or press the button to test...")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    encoder.cleanup()
    print("\nGoodbye!")
