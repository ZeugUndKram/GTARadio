#!/usr/bin/env python3
"""
KY-040 Rotary Encoder Handler for Raspberry Pi
Clean, modular implementation with event callbacks
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Callable, Optional

class RotaryEncoder:
    def __init__(self, clk_pin: int, dt_pin: int, sw_pin: Optional[int] = None):
        """
        Initialize rotary encoder
        
        Args:
            clk_pin: GPIO pin for CLK (Clock) signal
            dt_pin: GPIO pin for DT (Data) signal  
            sw_pin: GPIO pin for SW (Switch) button (optional)
        """
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        
        # Encoder state
        self.clk_last_state = 0
        self.counter = 0
        self.last_rotation_time = 0
        self.debounce_delay = 0.01  # 10ms debounce
        
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
        
        # Add interrupt detection on both encoder pins
        GPIO.add_event_detect(self.clk_pin, GPIO.BOTH, callback=self._rotation_callback, bouncetime=2)
        GPIO.add_event_detect(self.dt_pin, GPIO.BOTH, callback=self._rotation_callback, bouncetime=2)
        
        # Setup button if provided
        if self.sw_pin is not None:
            GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.sw_pin, GPIO.FALLING, 
                                callback=self._button_callback, bouncetime=300)
    
    def _rotation_callback(self, channel):
        """Handle rotary encoder rotation with debouncing"""
        current_time = time.time()
        
        # Debounce check
        if current_time - self.last_rotation_time < self.debounce_delay:
            return
            
        clk_state = GPIO.input(self.clk_pin)
        dt_state = GPIO.input(self.dt_pin)
        
        # Only process if state changed
        if clk_state != self.clk_last_state:
            self.last_rotation_time = current_time
            
            # Determine direction
            if dt_state != clk_state:
                direction = 1  # Clockwise
                self.counter += 1
            else:
                direction = -1  # Counter-clockwise
                self.counter -= 1
            
            # Call user callback if set
            if self.rotate_callback:
                self.rotate_callback(direction, self.counter)
            
        self.clk_last_state = clk_state
    
    def _button_callback(self, channel):
        """Handle button press"""
        if self.button_callback:
            self.button_callback()
    
    def on_rotate(self, callback: Callable[[int, int], None]):
        """
        Set callback for rotation events
        
        Args:
            callback: Function that receives (direction, counter)
                     direction: 1 for CW, -1 for CCW
                     counter: current cumulative position
        """
        self.rotate_callback = callback
    
    def on_button_press(self, callback: Callable[[], None]):
        """
        Set callback for button press events
        
        Args:
            callback: Function called when button is pressed
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

def init_encoder(clk_pin: int, dt_pin: int, sw_pin: Optional[int] = None) -> RotaryEncoder:
    """
    Initialize and return a global encoder instance
    
    Args:
        clk_pin: GPIO pin for CLK signal
        dt_pin: GPIO pin for DT signal
        sw_pin: GPIO pin for SW button (optional)
    
    Returns:
        RotaryEncoder instance
    """
    global _encoder_instance
    _encoder_instance = RotaryEncoder(clk_pin, dt_pin, sw_pin)
    return _encoder_instance

def get_encoder() -> RotaryEncoder:
    """
    Get the global encoder instance
    
    Returns:
        RotaryEncoder instance
    """
    if _encoder_instance is None:
        raise RuntimeError("Encoder not initialized. Call init_encoder() first.")
    return _encoder_instance
