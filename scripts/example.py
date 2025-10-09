#!/usr/bin/env python3
"""
Test script to verify rotation and button work separately
"""

import input
import time

encoder = input.get_encoder()

# Counter for tracking
rotation_count = 0
button_count = 0

def rotation_handler(direction, counter):
    global rotation_count
    rotation_count += 1
    direction_str = "CLOCKWISE" if direction == 1 else "COUNTER-CLOCKWISE"
    print(f"🎯 ROTATION #{rotation_count}: {direction_str} - Total: {counter}")

def button_handler():
    global button_count
    button_count += 1
    print(f"🔘 BUTTON #{button_count}: PRESSED")

encoder.on_rotate(rotation_handler)
encoder.on_button_press(button_handler)

print("=== ROTARY ENCODER TEST ===")
print("Pins: CLK=14, DT=15, SW=16")
print("TURN the knob → should show ROTATION messages")
print("PUSH the knob → should show BUTTON messages")
print("They should NOT interfere with each other!")
print("Press Ctrl+C to exit\n")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    encoder.cleanup()
    print(f"\nTest complete: {rotation_count} rotations, {button_count} button presses")
