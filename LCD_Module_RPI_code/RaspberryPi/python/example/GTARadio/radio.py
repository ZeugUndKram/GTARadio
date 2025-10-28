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

# Global playback position tracking
_current_playback_position = 0  # in seconds
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
    print("Cache cleared")

<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> parent of 36c7a70 (Update radio.py)
def set_music_mode(enabled):
    """Set music mode (True) or radio mode (False)"""
    global _music_mode
    _music_mode = enabled
    print(f"Music mode {'enabled' if enabled else 'disabled'}")

<<<<<<< HEAD

=======
>>>>>>> parent of 36c7a70 (Update radio.py)
def get_music_mode():
    """Get current music mode status"""
    return _music_mode

<<<<<<< HEAD

=======
>>>>>>> parent of 36c7a70 (Update radio.py)
def _stop_song_end_monitor():
    """Stop the song end monitoring thread"""
    global _song_end_running, _song_end_thread
    _song_end_running = False
    if _song_end_thread and _song_end_thread.is_alive():
        _song_end_thread.join(timeout=1.0)
        _song_end_thread = None

<<<<<<< HEAD

def _song_end_monitor():
    """Monitor for song end and play next song in music mode"""
    global _song_end_running, _music_mode

=======
def _song_end_monitor():
    """Monitor for song end and play next song in music mode"""
    global _song_end_running, _music_mode, _current_playback_position
    
>>>>>>> parent of 36c7a70 (Update radio.py)
    while _song_end_running and _music_mode:
        current_time = time.time()
        
        # Check if current song has ended
        if current_time >= _song_end_time:
            print("Song ended, playing next station in music mode")
            from main import next_station
            next_station()
            break
        
        time.sleep(0.1)  # Check every 100ms
<<<<<<< HEAD

=======
>>>>>>> parent of 36c7a70 (Update radio.py)

def play_radio(game_index, station_index):
    global mp3_process, _current_playback_position, _first_playback, _current_song_duration, _song_end_time
    global _song_end_thread, _song_end_running, _music_mode
<<<<<<< HEAD

=======
=======
def play_radio(game_index, station_index):
    global mp3_process, _current_playback_position, _first_playback
>>>>>>> parent of f9bb197 (Removed gif func added music setting)
    
>>>>>>> parent of 36c7a70 (Update radio.py)
    # Get available stations from cache
    stations, mp3_durations = get_radio_stations()

    if not stations:
        print("Error: No games/stations found")
        return

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
<<<<<<< HEAD
=======
    
    # Get duration of the selected song
    duration = mp3_durations.get(selected_song, 300)
    
    # Calculate start position
    if _first_playback:
        # First playback: use random position
        start_position = random.uniform(0, duration)
        _first_playback = False
        print(f"First playback: random start at {start_position:.2f}s")
    else:
        # Subsequent playbacks: continue from last position (wrap around if needed)
        start_position = _current_playback_position % duration
        print(f"Continuing playback at {start_position:.2f}s (wrapped from {_current_playback_position:.2f}s)")
    
    # Update global position for next switch
    _current_playback_position = start_position
    
    # Convert to frames (mpg123 uses 75 frames per second)
    start_frame = int(start_position * 75)
    
<<<<<<< HEAD
    print(f"Playing {os.path.basename(selected_song)} from {start_position:.2f}s (frame {start_frame}) - Duration: {_current_song_duration}s - Mode: {'Music' if _music_mode else 'Radio'}")
>>>>>>> parent of 36c7a70 (Update radio.py)

    _current_song_duration = mp3_durations.get(selected_song, 300)
    
    if _music_mode:
        start_position = 0
        print(f"Music mode: starting from beginning (0s)")
        _first_playback = False
    else:
        if _first_playback:
            start_position = random.uniform(0, _current_song_duration)
            _first_playback = False
            print(f"Radio mode: random start at {start_position:.2f}s")
        else:
            start_position = _current_playback_position % _current_song_duration
            print(f"Radio mode: continuing at {start_position:.2f}s (wrapped from {_current_playback_position:.2f}s)")

    _current_playback_position = start_position
    
    if _music_mode:
        _song_end_time = time.time() + (_current_song_duration - start_position)
        print(f"Song will end at: {time.ctime(_song_end_time)}")

    start_frame = int(start_position * 75)
    print(f"Playing {os.path.basename(selected_song)} from {start_position:.2f}s "
          f"(frame {start_frame}) - Duration: {_current_song_duration}s - Mode: {'Music' if _music_mode else 'Radio'}")
=======
    print(f"Playing {os.path.basename(selected_song)} from {start_position:.2f}s (frame {start_frame}) - Duration: {duration}s")
>>>>>>> parent of f9bb197 (Removed gif func added music setting)

    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

<<<<<<< HEAD
<<<<<<< HEAD
    _stop_song_end_monitor()

=======
    # Stop previous song end monitor
    _stop_song_end_monitor()

=======
>>>>>>> parent of f9bb197 (Removed gif func added music setting)
    # Start playback with suppressed output
>>>>>>> parent of 36c7a70 (Update radio.py)
    try:
        mp3_process = subprocess.Popen(
            ['mpg123', '-k', str(start_frame), selected_song],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
<<<<<<< HEAD
        
<<<<<<< HEAD
=======
        # Start song end monitoring thread if in music mode
>>>>>>> parent of 36c7a70 (Update radio.py)
        if _music_mode:
            _song_end_running = True
            _song_end_thread = threading.Thread(target=_song_end_monitor, daemon=True)
            _song_end_thread.start()
            print("Started song end monitor")
            
=======
>>>>>>> parent of f9bb197 (Removed gif func added music setting)
    except Exception as e:
        print(f"Error starting playback: {e}")

<<<<<<< HEAD

=======
>>>>>>> parent of 36c7a70 (Update radio.py)
def update_playback_position():
    """Update the current playback position based on elapsed time"""
<<<<<<< HEAD
    global _current_playback_position, _music_mode
    if not _first_playback and not _music_mode:
<<<<<<< HEAD
        _current_playback_position += 0.1  # Update every 100ms

=======
        # Only update position in radio mode (in music mode we use actual file position)
=======
    global _current_playback_position
    if not _first_playback:
        # Increment position by small amount to simulate progress
        # Note: This is approximate since we don't have exact position from mpg123
>>>>>>> parent of f9bb197 (Removed gif func added music setting)
        _current_playback_position += 0.1  # Update every 100ms
>>>>>>> parent of 36c7a70 (Update radio.py)

def reset_playback_position():
    """Reset to first playback mode (for when stopping/starting fresh)"""
    global _first_playback, _current_playback_position
    _first_playback = True
    _current_playback_position = 0
    print("Playback position reset")
<<<<<<< HEAD


def get_current_position():
    """Get the current playback position"""
    return _current_playback_position
=======

def get_current_position():
    """Get the current playback position"""
    return _current_playback_position
>>>>>>> parent of 36c7a70 (Update radio.py)
