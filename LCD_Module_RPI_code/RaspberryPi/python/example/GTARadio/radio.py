import subprocess
import random
import os
import time

mp3_process = None
SHARED_BASE_PATH = '/mnt/shared/gta/'

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
            
            # Get duration (using default for now)
            mp3_durations[file_path] = 300  # Default 5 minutes
    
    print(f"Cache updated: Found {len(stations)} games with stations")
    
    # Update cache
    _stations_cache = stations
    _mp3_durations_cache = mp3_durations
    _last_cache_update = current_time
    
    return stations, mp3_durations

def clear_cache():
    """Clear the cache to force refresh on next call"""
    global _stations_cache, _mp3_durations_cache, _last_cache_update
    _stations_cache = None
    _mp3_durations_cache = None
    _last_cache_update = 0
    print("Cache cleared")

def play_radio(game_index, station_index):
    global mp3_process
    
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
    
    # Terminate existing process
    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

    # Get duration and calculate random start
    duration = mp3_durations.get(selected_song, 300)
    random_start_frame = int(random.uniform(0, duration) * 75)

    print(f"Playing {selected_song} from frame {random_start_frame}")

    # Start playback with suppressed output
    try:
        mp3_process = subprocess.Popen(
            ['mpg123', '-k', str(random_start_frame), selected_song],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error starting playback: {e}")