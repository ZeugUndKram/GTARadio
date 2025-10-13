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
        self.settings_list = []
        self.load_settings()
    
    def load_settings(self):
        """Load available settings from assets folder"""
        if not os.path.exists(ASSETS_PATH):
            os.makedirs(ASSETS_PATH, exist_ok=True)
        
        # Define expected settings images
        self.settings_list = [
            {'name': 'playlist', 'image': 'playlist.png', 'type': 'menu'},
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
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        print("Shutting down system...")
        try:
            # Stop playback first
            self.stop_playback()
            
            # Display shutdown message
            self.show_shutdown_message()
            
            # Wait a moment for the message to be seen
            import time
            time.sleep(2)
            
            # Execute shutdown command
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            return 'shutdown'
        except Exception as e:
            print(f"Error during shutdown: {e}")
            return None
    
    def show_shutdown_message(self):
        """Display shutdown message"""
        try:
            from display import show_default_image
            # Create a shutdown message screen
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
                print(f"Setting: {setting['name']}")
    
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