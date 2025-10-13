import os
import sys
import subprocess
from display import display_image, show_default_image
from radio import get_radio_stations, mp3_process

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')

class SettingsManager:
    def __init__(self):
        self.in_settings = False
        self.in_playlist_select = False
        self.current_setting_index = 0
        self.current_playlist_index = 0
        self.current_brightness_index = 0  # 0-4 for hell_0 to hell_4
        self.settings_list = []
        self.load_settings()
        self.load_brightness_level()
    
    def load_settings(self):
        """Load available settings from assets folder"""
        if not os.path.exists(ASSETS_PATH):
            os.makedirs(ASSETS_PATH, exist_ok=True)
        
        # Define expected settings images
        self.settings_list = [
            {'name': 'playlist', 'image': 'playlist.png', 'type': 'menu'},
            {'name': 'brightness', 'image': 'hell_0.png', 'type': 'action'},  # Will be updated dynamically
            {'name': 'shutdown', 'image': 'Aus.png', 'type': 'action'}
        ]
        
        # Check which images actually exist and update brightness image
        available_settings = []
        for setting in self.settings_list:
            if setting['name'] == 'brightness':
                # Use current brightness level image
                brightness_image = f"hell_{self.current_brightness_index}.png"
                setting['image'] = brightness_image
            
            image_path = os.path.join(ASSETS_PATH, setting['image'])
            if os.path.exists(image_path):
                available_settings.append(setting)
            else:
                print(f"Warning: Settings image not found: {image_path}")
        
        self.settings_list = available_settings
    
    def load_brightness_level(self):
        """Load the current brightness level from storage"""
        try:
            brightness_file = os.path.join(os.path.dirname(__file__), 'brightness_level.txt')
            if os.path.exists(brightness_file):
                with open(brightness_file, 'r') as f:
                    self.current_brightness_index = int(f.read().strip())
                    # Ensure it's within bounds
                    self.current_brightness_index = max(0, min(4, self.current_brightness_index))
            else:
                self.current_brightness_index = 2  # Default medium brightness
                self.save_brightness_level()
        except Exception as e:
            print(f"Error loading brightness level: {e}")
            self.current_brightness_index = 2
    
    def save_brightness_level(self):
        """Save the current brightness level to storage"""
        try:
            brightness_file = os.path.join(os.path.dirname(__file__), 'brightness_level.txt')
            with open(brightness_file, 'w') as f:
                f.write(str(self.current_brightness_index))
        except Exception as e:
            print(f"Error saving brightness level: {e}")
    
    def set_brightness(self, brightness_index):
        """Set the display brightness using alternative method"""
        try:
            # Map brightness index to actual brightness values
            brightness_values = [50, 100, 150, 200, 255]  # hell_0 to hell_4
            brightness_value = brightness_values[brightness_index]
            
            # Try different methods to set brightness
            
            # Method 1: Try Raspberry Pi backlight control
            try:
                backlight_path = '/sys/class/backlight/10-0045/brightness'
                if os.path.exists(backlight_path):
                    with open(backlight_path, 'w') as f:
                        f.write(str(brightness_value))
                    print(f"Set brightness via backlight control: {brightness_value}")
                else:
                    # Try other common backlight paths
                    backlight_dirs = ['/sys/class/backlight/']
                    for backlight_dir in backlight_dirs:
                        if os.path.exists(backlight_dir):
                            for device in os.listdir(backlight_dir):
                                device_path = os.path.join(backlight_dir, device, 'brightness')
                                if os.path.exists(device_path):
                                    with open(device_path, 'w') as f:
                                        f.write(str(brightness_value))
                                    print(f"Set brightness via {device_path}: {brightness_value}")
                                    break
            except Exception as e:
                print(f"Backlight control failed: {e}")
            
            # Method 2: Try using display library if available
            try:
                import os
                import sys
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
                from lib import LCD_1inch28
                
                # Reinitialize display with new brightness if supported
                disp = LCD_1inch28.LCD_1inch28()
                disp.Init()
                
                # If the display library has a brightness method, use it
                if hasattr(disp, 'set_brightness'):
                    disp.set_brightness(brightness_value)
                    print(f"Set brightness via display library: {brightness_value}")
            except Exception as e:
                print(f"Display library brightness control failed: {e}")
            
            # Method 3: Try GPIO PWM as last resort
            try:
                import RPi.GPIO as GPIO
                BL = 18  # Backlight pin
                
                GPIO.setup(BL, GPIO.OUT)
                pwm = GPIO.PWM(BL, 1000)  # 1kHz frequency
                pwm.start(brightness_value)
                print(f"Set brightness via GPIO PWM: {brightness_value}")
            except Exception as e:
                print(f"GPIO PWM brightness control failed: {e}")
            
            print(f"Set brightness to level {brightness_index} (value: {brightness_value})")
            
            # Save the brightness level
            self.current_brightness_index = brightness_index
            self.save_brightness_level()
            
            # Update the settings list with new brightness image
            self.update_brightness_setting()
            
            return True
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False
    
    def update_brightness_setting(self):
        """Update the brightness setting with current level image"""
        for setting in self.settings_list:
            if setting['name'] == 'brightness':
                setting['image'] = f"hell_{self.current_brightness_index}.png"
                break
    
    def next_brightness(self):
        """Cycle to next brightness level"""
        new_brightness_index = (self.current_brightness_index + 1) % 5  # 0-4
        success = self.set_brightness(new_brightness_index)
        if success:
            # Update the display if we're currently viewing brightness
            if (self.in_settings and not self.in_playlist_select and 
                self.settings_list[self.current_setting_index]['name'] == 'brightness'):
                self.show_current_setting()
            return True
        return False
    
    def stop_playback(self):
        """Stop any ongoing playback"""
        global mp3_process
        if mp3_process and mp3_process.poll() is None:
            mp3_process.terminate()
            mp3_process.wait()
            print("Playback stopped")
    
    def enter_settings(self):
        """Enter settings mode"""
        self.stop_playback()  # Stop playback when entering settings
        self.in_settings = True
        self.in_playlist_select = False
        self.current_setting_index = 0
        self.show_current_setting()
        print("Entered settings mode - playback stopped")
    
    def exit_settings(self):
        """Exit settings mode"""
        self.in_settings = False
        self.in_playlist_select = False
        print("Exited settings mode")
        return True
    
    def enter_playlist_select(self):
        """Enter playlist selection mode"""
        if self.current_setting_index == 0:  # playlist.png selected
            self.in_playlist_select = True
            self.current_playlist_index = 0
            self.show_current_playlist()
            print("Entered playlist selection")
            return True
        return False
    
    def show_shutdown_image(self):
        """Display Shutdown.png image"""
        try:
            shutdown_image_path = os.path.join(ASSETS_PATH, 'Shutdown.png')
            if os.path.exists(shutdown_image_path):
                # Use the display_image function with special parameters for shutdown
                # We'll use game_index=-2 to indicate shutdown screen
                display_image(-2, 0)
                print("Displayed Shutdown.png")
            else:
                # Fallback to text message if Shutdown.png doesn't exist
                self.show_shutdown_message()
        except Exception as e:
            print(f"Error displaying shutdown image: {e}")
            self.show_shutdown_message()
    
    def show_shutdown_message(self):
        """Display shutdown message as fallback"""
        try:
            from display import show_default_image
            import os
            import sys
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            from lib import LCD_1inch28
            from PIL import Image, ImageDraw, ImageFont
            
            disp = LCD_1inch28.LCD_1inch28()
            disp.Init()
            
            image = Image.new('RGB', (240, 240), color='red')
            draw = ImageDraw.Draw(image)
            
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            draw.text((120, 100), "SHUTTING DOWN", fill='white', font=font_large, anchor="mm")
            draw.text((120, 130), "Goodbye!", fill='white', font=font_small, anchor="mm")
            
            im_r = image.rotate(0)
            disp.ShowImage(im_r)
        except Exception as e:
            print(f"Error showing shutdown message: {e}")
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        print("Shutting down system...")
        try:
            # Stop playback first
            self.stop_playback()
            
            # Display Shutdown.png image
            self.show_shutdown_image()
            
            # Wait a moment for the image to be seen
            import time
            time.sleep(3)
            
            # Execute shutdown command
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            return 'shutdown'
        except Exception as e:
            print(f"Error during shutdown: {e}")
            return None
    
    def next_setting(self):
        """Move to next setting"""
        if self.settings_list:
            self.current_setting_index = (self.current_setting_index + 1) % len(self.settings_list)
            self.show_current_setting()
    
    def previous_setting(self):
        """Move to previous setting"""
        if self.settings_list:
            self.current_setting_index = (self.current_setting_index - 1) % len(self.settings_list)
            self.show_current_setting()
    
    def next_playlist(self):
        """Move to next playlist"""
        stations, _ = get_radio_stations()
        if stations:
            game_folders = sorted(stations.keys())
            self.current_playlist_index = (self.current_playlist_index + 1) % len(game_folders)
            self.show_current_playlist()
    
    def previous_playlist(self):
        """Move to previous playlist"""
        stations, _ = get_radio_stations()
        if stations:
            game_folders = sorted(stations.keys())
            self.current_playlist_index = (self.current_playlist_index - 1) % len(game_folders)
            self.show_current_playlist()
    
    def show_current_setting(self):
        """Display current setting image"""
        if self.settings_list and not self.in_playlist_select:
            setting = self.settings_list[self.current_setting_index]
            image_path = os.path.join(ASSETS_PATH, setting['image'])
            if os.path.exists(image_path):
                # Use special display mode for settings
                display_image(-1, self.current_setting_index)
                print(f"Setting: {setting['name']} (level: {self.current_brightness_index})")
    
    def show_current_playlist(self):
        """Display current playlist cover or name"""
        stations, _ = get_radio_stations()
        if stations:
            game_folders = sorted(stations.keys())
            if self.current_playlist_index < len(game_folders):
                game_name = game_folders[self.current_playlist_index]
                
                # Try to display the game logo, fall back to name display
                display_image(self.current_playlist_index, 0)  # 0 = game logo
                print(f"Select playlist: {game_name}")
    
    def select_current_playlist(self):
        """Select the currently displayed playlist (without starting playback)"""
        if self.in_playlist_select:
            stations, _ = get_radio_stations()
            if stations:
                game_folders = sorted(stations.keys())
                if self.current_playlist_index < len(game_folders):
                    selected_game_index = self.current_playlist_index
                    game_name = game_folders[selected_game_index]
                    self.exit_settings()
                    print(f"Selected playlist: {game_name} (playback not started)")
                    return selected_game_index
        return None
    
    def handle_space(self):
        """Handle space bar press in different modes"""
        if not self.in_settings:
            # Enter settings mode (stops playback)
            self.enter_settings()
            return 'enter_settings'
        
        elif self.in_settings and not self.in_playlist_select:
            # Check which setting is selected
            current_setting = self.settings_list[self.current_setting_index]
            
            if current_setting['name'] == 'playlist':
                # Enter submenu (playlist selection)
                if self.enter_playlist_select():
                    return 'enter_playlist_select'
            
            elif current_setting['name'] == 'brightness':
                # Cycle brightness level
                if self.next_brightness():
                    return 'brightness_changed'
            
            elif current_setting['name'] == 'shutdown':
                # Execute shutdown
                return self.execute_shutdown()
        
        elif self.in_playlist_select:
            # Select current playlist and exit (without starting playback)
            selected_game = self.select_current_playlist()
            if selected_game is not None:
                return ('select_playlist', selected_game)
        
        return None
    
    def handle_escape(self):
        """Handle escape/back navigation"""
        if self.in_playlist_select:
            # Back to settings menu
            self.in_playlist_select = False
            self.show_current_setting()
            return 'back_to_settings'
        elif self.in_settings:
            # Exit settings completely
            self.exit_settings()
            return 'exit_settings'
        return None

# Global settings manager instance
settings_manager = SettingsManager()