#!/usr/bin/env python3
"""
Example usage of the rotary encoder handler
"""

import input

import time
import signal
import sys

def rotation_handler(direction, counter):
    """Handle rotation events"""
    direction_str = "CLOCKWISE" if direction == 1 else "COUNTER-CLOCKWISE"
    print(f"Rotation: {direction_str} | Counter: {counter}")

def button_handler():
    """Handle button press events"""
    print("Button pressed!")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    encoder.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize encoder (replace with your actual GPIO pins)
    # CLK=17, DT=18, SW=27 are common examples
    encoder = input.init_encoder(clk_pin=17, dt_pin=18, sw_pin=27)
    
    # Set up event handlers
    encoder.on_rotate(rotation_handler)
    encoder.on_button_press(button_handler)
    
    print("Rotary encoder handler started!")
    print("Turn the encoder or press the button to test.")
    print("Press Ctrl+C to exit.\n")
    
    # Keep the program running
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(None, None)
