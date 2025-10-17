import subprocess
import random
import os
import time
import math

mp3_process = None
SHARED_BASE_PATH = '/mnt/shared/gta/'

# Cache variables
_stations_cache = None
_mp3_durations_cache = None
_last_cache_update = 0
CACHE_TIMEOUT = 30  # seconds

# Global progress tracking - NEW SYSTEM
_global_radio_time = 0.0  # Continuous radio timeline in seconds
_current_station_start_time = None
_current_station_path = None
_first_playback = True

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
        # Try using mutagen to get duration
        from mutagen import File
        audio = File(mp3_path)
        if audio is not None and hasattr(audio, 'info'):
            duration = audio.info.length
            print(f"Found duration for {os.path.basename(mp3_path)}: {duration:.2f}s")
            return math.ceil(duration)
    except Exception as e:
        print(f"Could not get duration for {mp3_path}: {e}")
    
    # Fallback to default duration
    return 300  # Default 5 minutes

def clear_cache():
    """Clear the cache to force refresh on next call"""
    global _stations_cache, _mp3_durations_cache, _last_cache_update
    _stations_cache = None
    _mp3_durations_cache = None
    _last_cache_update = 0
    reset_playback_position()  # Also reset the radio timeline
    print("Cache and progress tracking cleared")

def play_radio(game_index, station_index):
    global mp3_process, _global_radio_time, _current_station_start_time, _current_station_path, _first_playback
    
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
    
    # Get duration of the selected song
    duration = mp3_durations.get(selected_song, 300)
    current_time = time.time()
    
    # If we were playing another station, add that listening time to global progress
    if _current_station_start_time and _current_station_path != selected_song:
        listen_duration = current_time - _current_station_start_time
        _global_radio_time += listen_duration
        print(f"Added {listen_duration:.1f}s to radio timeline (total: {_global_radio_time:.1f}s)")
    
    # Calculate start position for this station
    if _first_playback:
        # First ever playback - random start
        start_position = random.uniform(0, duration)
        _global_radio_time = start_position  # Initialize timeline
        _first_playback = False
        print(f"First playback: random start at {start_position:.1f}s")
    else:
        # Continue from global radio timeline (with wrap-around)
        start_position = _global_radio_time % duration
        print(f"Continuing at {start_position:.1f}s (radio time: {_global_radio_time:.1f}s)")
    
    # Update tracking for current station
    _current_station_start_time = current_time
    _current_station_path = selected_song
    
    # Convert to frames (mpg123 uses 75 frames per second)
    start_frame = int(start_position * 75)
    
    print(f"Playing {os.path.basename(selected_song)} from {start_position:.2f}s (frame {start_frame}) - Duration: {duration}s")

    # Terminate existing process
    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

    # Start playback with suppressed output
    try:
        mp3_process = subprocess.Popen(
            ['mpg123', '-k', str(start_frame), selected_song],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error starting playback: {e}")

# REMOVED: update_playback_position() function - no longer needed

def reset_playback_position():
    """Reset to first playback mode (for when stopping/starting fresh)"""
    global _first_playback, _global_radio_time, _current_station_start_time, _current_station_path
    _first_playback = True
    _global_radio_time = 0.0
    _current_station_start_time = None
    _current_station_path = None
    print("Playback position and radio timeline reset")

def get_current_position():
    """Get the current playback position in the currently playing station"""
    if _current_station_start_time and _current_station_path:
        stations, mp3_durations = get_radio_stations()
        duration = mp3_durations.get(_current_station_path, 300)
        current_time = time.time()
        station_elapsed = current_time - _current_station_start_time
        return (_global_radio_time + station_elapsed) % duration
    return 0

def get_radio_timeline():
    """Get the current global radio timeline position"""
    return _global_radio_time