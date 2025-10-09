#!/usr/bin/env python3
"""
KY-040 Rotary Encoder Handler for Raspberry Pi
Fixed version with proper rotation detection
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Callable, Optional

class RotaryEncoder:
    def __init__(self, clk_pin: int = 14, dt_pin: int = 15, sw_pin: Optional[int] = 16):
        """
        Initialize rotary encoder with default pins 14, 15, 16
        """
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        
        # Encoder state
        self.clk_last_state = 0
        self.counter = 0
        self.last_rotation_time = 0
        self.debounce_delay = 0.002  # Reduced debounce for better response
        
        # Callback functions
        self.rotate_callback = None
        self.button_callback = None
        
        # Setup GPIO
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Configure GPIO pins and interrupts"""
        GPIO.setmode(GPIO.BCM)
        
        # Setup encoder pins with pull-up resistors
        GPIO.setup(self.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Get initial state
        self.clk_last_state = GPIO.input(self.clk_pin)
        
        # Add interrupt detection on CLK pin only (fixes the issue)
        GPIO.add_event_detect(self.clk_pin, GPIO.FALLING, 
                            callback=self._rotation_callback, 
                            bouncetime=5)
        
        # Setup button if provided - use longer debounce
        if self.sw_pin is not None:
            GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.sw_pin, GPIO.FALLING, 
                                callback=self._button_callback, 
                                bouncetime=500)  # Longer debounce for button
    
    def _rotation_callback(self, channel):
        """Handle rotary encoder rotation - FIXED VERSION"""
        # Read both pins when CLK detects falling edge
        clk_state = GPIO.input(self.clk_pin)
        dt_state = GPIO.input(self.dt_pin)
        
        # Only process if CLK is low (falling edge)
        if clk_state == 0:
            if dt_state == 1:
                # Clockwise rotation
                direction = 1
                self.counter += 1
            else:
                # Counter-clockwise rotation  
                direction = -1
                self.counter -= 1
            
            # Call user callback if set
            if self.rotate_callback:
                self.rotate_callback(direction, self.counter)
    
    def _button_callback(self, channel):
        """Handle button press - only called for actual button"""
        # Double-check it's really the button by reading the pin
        if GPIO.input(self.sw_pin) == 0:  # Button is pressed (active low)
            if self.button_callback:
                self.button_callback()
    
    def on_rotate(self, callback: Callable[[int, int], None]):
        """
        Set callback for rotation events
        """
        self.rotate_callback = callback
    
    def on_button_press(self, callback: Callable[[], None]):
        """
        Set callback for button press events
        """
        self.button_callback = callback
    
    def get_count(self) -> int:
        """Get current encoder counter value"""
        return self.counter
    
    def reset_count(self):
        """Reset encoder counter to zero"""
        self.counter = 0
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup([self.clk_pin, self.dt_pin] + 
                    ([self.sw_pin] if self.sw_pin else []))


# Global encoder instance for easy importing
_encoder_instance = None

def init_encoder(clk_pin: int = 14, dt_pin: int = 15, sw_pin: Optional[int] = 16) -> RotaryEncoder:
    """
    Initialize and return a global encoder instance
    """
    global _encoder_instance
    _encoder_instance = RotaryEncoder(clk_pin, dt_pin, sw_pin)
    return _encoder_instance

def get_encoder() -> RotaryEncoder:
    """
    Get the global encoder instance
    """
    if _encoder_instance is None:
        return init_encoder()
    return _encoder_instance
