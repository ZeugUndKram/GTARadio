import subprocess
import random
import os
import time

mp3_process = None
SHARED_BASE_PATH = '/mnt/shared/gta/'

# Track current playback position for radio mode
current_playback_position = 0  # in seconds
last_playback_time = 0
last_mp3_path = None

# Cache variables
_stations_cache = None
_mp3_durations_cache = None
_last_cache_update = 0
CACHE_TIMEOUT = 30  # seconds

def get_radio_stations(force_refresh=False):
    """Dynamically discover all games and their radio stations with caching"""
    global _stations_cache, _mp3_durations_cache, _last_cache_update
    
    current_time = time.time()
    
    # Return cached data if it's fresh and not forced to refresh
    if (not force_refresh and 
        _stations_cache is not None and 
        _mp3_durations_cache is not None and
        current_time - _last_cache_update < CACHE_TIMEOUT):
        return _stations_cache, _mp3_durations_cache
    
    stations = {}
    mp3_durations = {}
    
    if not os.path.exists(SHARED_BASE_PATH):
        print(f"Shared path not found: {SHARED_BASE_PATH}")
        return stations, mp3_durations
    
    # Each folder in shared path is a game
    game_folders = [f for f in os.listdir(SHARED_BASE_PATH) 
                   if os.path.isdir(os.path.join(SHARED_BASE_PATH, f))]
    
    if not game_folders:
        print("No game folders found")
        return stations, mp3_durations
    
    for game_folder in sorted(game_folders):
        game_path = os.path.join(SHARED_BASE_PATH, game_folder)
        stations[game_folder] = []
        
        # Find all MP3 files in the game folder
        try:
            mp3_files = [f for f in os.listdir(game_path) if f.lower().endswith('.mp3')]
        except PermissionError:
            print(f"Permission denied accessing: {game_path}")
            continue
            
        if not mp3_files:
            print(f"No MP3 files found in {game_folder}")
            continue
            
        for file in sorted(mp3_files):
            station_name = os.path.splitext(file)[0]
            file_path = os.path.join(game_path, file)
            stations[game_folder].append({
                'name': station_name,
                'mp3_path': file_path
            })
            
            # Get actual duration if possible, otherwise use default
            duration = get_mp3_duration(file_path)
            mp3_durations[file_path] = duration
    
    print(f"Cache updated: Found {len(stations)} games with stations")
    
    # Update cache
    _stations_cache = stations
    _mp3_durations_cache = mp3_durations
    _last_cache_update = current_time
    
    return stations, mp3_durations

def get_mp3_duration(mp3_path):
    """Get the actual duration of an MP3 file in seconds"""
    try:
        # Try to use mutagen to get actual duration
        from mutagen import File
        audio = File(mp3_path)
        if audio is not None and hasattr(audio, 'info'):
            duration = int(audio.info.length)
            print(f"Found actual duration for {mp3_path}: {duration} seconds")
            return duration
    except:
        pass
    
    # Fallback to default duration
    print(f"Using default duration for {mp3_path}")
    return 300  # Default 5 minutes

def get_current_playback_mode():
    """Get the current playback mode from settings"""
    try:
        from settings import settings_manager
        return settings_manager.current_playback_mode
    except:
        return 'radio'  # Default to radio mode

def update_playback_position():
    """Update the current playback position based on elapsed time"""
    global current_playback_position, last_playback_time, last_mp3_path
    
    if last_mp3_path and last_playback_time > 0:
        elapsed_time = time.time() - last_playback_time
        current_playback_position += elapsed_time
        
        # Get the duration of the last played MP3
        _, mp3_durations = get_radio_stations()
        duration = mp3_durations.get(last_mp3_path, 300)
        
        # In radio mode, loop using modulo
        if get_current_playback_mode() == 'radio':
            current_playback_position = current_playback_position % duration
        # In song mode, don't update position after song ends
        elif current_playback_position > duration:
            current_playback_position = duration
        
        print(f"Updated playback position: {current_playback_position:.1f}s (duration: {duration}s)")
    
    last_playback_time = time.time()

def clear_cache():
    """Clear the cache to force refresh on next call"""
    global _stations_cache, _mp3_durations_cache, _last_cache_update
    _stations_cache = None
    _mp3_durations_cache = None
    _last_cache_update = 0
    print("Cache cleared")

def play_radio(game_index, station_index):
    global mp3_process, current_playback_position, last_playback_time, last_mp3_path
    
    # Update playback position before switching
    if mp3_process and mp3_process.poll() is None:
        update_playback_position()
    
    # Get available stations from cache
    stations, mp3_durations = get_radio_stations()
    
    if not stations:
        print("Error: No games/stations found")
        return
    
    # Convert indices to lists for access
    game_folders = sorted(stations.keys())
    
    if game_index >= len(game_folders):
        print(f"Error: Game index {game_index} out of range. Available games: {len(game_folders)}")
        return
    
    game_name = game_folders[game_index]
    game_stations = stations[game_name]
    
    if not game_stations:
        print(f"Error: No stations found in game {game_name}")
        return
    
    if station_index >= len(game_stations):
        print(f"Error: Station index {station_index} out of range. Available stations: {len(game_stations)}")
        return
    
    selected_station = game_stations[station_index]
    selected_song = selected_station['mp3_path']
    last_mp3_path = selected_song
    
    # Terminate existing process
    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

    # Get duration
    duration = mp3_durations.get(selected_song, 300)
    
    # Determine start position based on playback mode
    playback_mode = get_current_playback_mode()
    
    if playback_mode == 'radio':
        # Continue from current playback position (modulo duration for looping)
        start_position = current_playback_position % duration
        print(f"Radio mode: Continuing from position {start_position:.1f}s (current: {current_playback_position:.1f}s)")
    else:  # song mode
        # Always start from beginning
        start_position = 0
        current_playback_position = 0  # Reset position for song mode
        print("Song mode: Starting from beginning")
    
    # Convert to frames (1 frame = 1/75 second)
    start_frame = int(start_position * 75)
    
    print(f"Playing {selected_song} from frame {start_frame} (mode: {playback_mode})")

    # Start playback with suppressed output
    try:
        mp3_process = subprocess.Popen(
            ['mpg123', '-k', str(start_frame), selected_song],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        last_playback_time = time.time()
    except Exception as e:
        print(f"Error starting playback: {e}")

def play_next_song():
    """Play the next song in song mode (called when current song ends)"""
    global current_playback_position
    
    playback_mode = get_current_playback_mode()
    if playback_mode != 'song':
        return
    
    # Import here to avoid circular imports
    from main import game_index, station_index, next_station
    
    print("Song ended, playing next song...")
    
    # Reset position for next song
    current_playback_position = 0
    
    # Play next station
    next_station()

# Function to monitor playback and handle song mode transitions
def start_playback_monitor():
    """Start a background thread to monitor playback and handle song mode transitions"""
    import threading
    
    def monitor_playback():
        while True:
            try:
                if mp3_process and mp3_process.poll() is not None:
                    # Playback has ended
                    if get_current_playback_mode() == 'song':
                        play_next_song()
                time.sleep(1)
            except Exception as e:
                print(f"Error in playback monitor: {e}")
                time.sleep(5)
    
    monitor_thread = threading.Thread(target=monitor_playback, daemon=True)
    monitor_thread.start()
    print("Started playback monitor")