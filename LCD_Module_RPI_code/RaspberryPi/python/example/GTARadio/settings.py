import os
import sys
import subprocess
from display import display_image, show_default_image, clear_display_cache
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
        self.load_brightness_level()
        self.load_settings()  # Load settings AFTER brightness level
    
    def load_settings(self):
        """Load available settings from assets folder"""
        if not os.path.exists(ASSETS_PATH):
            os.makedirs(ASSETS_PATH, exist_ok=True)
        
        # Define expected settings images - brightness image will be dynamic
        self.settings_list = [
            {'name': 'playlist', 'image': 'playlist.png', 'type': 'menu'},
            {'name': 'brightness', 'image': f'hell_{self.current_brightness_index}.png', 'type': 'action'},
            {'name': 'shutdown', 'image': 'Aus.png', 'type': 'action'}
        ]
        
        # Check which images actually exist
        available_settings = []
        for setting in self.settings_list:
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
                    print(f"Loaded brightness level: {self.current_brightness_index}")
            else:
                self.current_brightness_index = 2  # Default medium brightness
                self.save_brightness_level()
                print(f"Created default brightness level: {self.current_brightness_index}")
        except Exception as e:
            print(f"Error loading brightness level: {e}")
            self.current_brightness_index = 2
    
    def save_brightness_level(self):
        """Save the current brightness level to storage"""
        try:
            brightness_file = os.path.join(os.path.dirname(__file__), 'brightness_level.txt')
            with open(brightness_file, 'w') as f:
                f.write(str(self.current_brightness_index))
            print(f"Saved brightness level: {self.current_brightness_index}")
        except Exception as e:
            print(f"Error saving brightness level: {e}")
    
    def next_brightness(self):
        """Cycle to next brightness level"""
        new_brightness_index = (self.current_brightness_index + 1) % 5  # 0-4
        print(f"Cycling brightness from {self.current_brightness_index} to {new_brightness_index}")
        
        # Update brightness level
        self.current_brightness_index = new_brightness_index
        self.save_brightness_level()
        
        # Update the settings list with new brightness image
        self.update_brightness_setting()
        
        # Clear display cache to force redraw of all images with new brightness
        clear_display_cache()
        
        # Refresh current display
        if self.in_settings and not self.in_playlist_select:
            self.show_current_setting()
        
        return True
    
    def update_brightness_setting(self):
        """Update the brightness setting with current level image"""
        print(f"Updating brightness setting to hell_{self.current_brightness_index}.png")
        if len(self.settings_list) > 1:  # Ensure brightness setting exists
            self.settings_list[1]['image'] = f"hell_{self.current_brightness_index}.png"
    
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
                display_image(-2, 0)
                print("Displayed Shutdown.png")
            else:
                self.show_shutdown_message()
        except Exception as e:
            print(f"Error displaying shutdown image: {e}")
            self.show_shutdown_message()
    
    def show_shutdown_message(self):
        """Display shutdown message as fallback"""
        try:
            show_default_image()
        except Exception as e:
            print(f"Error showing shutdown message: {e}")
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        print("Shutting down system...")
        try:
            self.stop_playback()
            self.show_shutdown_image()
            import time
            time.sleep(3)
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
            display_image(-1, self.current_setting_index)
            print(f"Setting: {setting['name']} (level: {self.current_brightness_index})")
    
    def show_current_playlist(self):
        """Display current playlist cover or name"""
        stations, _ = get_radio_stations()
        if stations:
            game_folders = sorted(stations.keys())
            if self.current_playlist_index < len(game_folders):
                game_name = game_folders[self.current_playlist_index]
                display_image(self.current_playlist_index, 0)
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
            self.enter_settings()
            return 'enter_settings'
        
        elif self.in_settings and not self.in_playlist_select:
            current_setting = self.settings_list[self.current_setting_index]
            
            if current_setting['name'] == 'playlist':
                if self.enter_playlist_select():
                    return 'enter_playlist_select'
            
            elif current_setting['name'] == 'brightness':
                if self.next_brightness():
                    return 'brightness_changed'
            
            elif current_setting['name'] == 'shutdown':
                return self.execute_shutdown()
        
        elif self.in_playlist_select:
            selected_game = self.select_current_playlist()
            if selected_game is not None:
                return ('select_playlist', selected_game)
        
        return None
    
    def handle_escape(self):
        """Handle escape/back navigation"""
        if self.in_playlist_select:
            self.in_playlist_select = False
            self.show_current_setting()
            return 'back_to_settings'
        elif self.in_settings:
            self.exit_settings()
            return 'exit_settings'
        return None

# Global settings manager instance
settings_manager = SettingsManager()