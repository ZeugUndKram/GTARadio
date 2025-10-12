import subprocess
import random
import time
import threading

mp3_process = None
play_thread = None
stop_thread = False

# Dictionary to store the duration of each MP3 file in seconds
mp3_durations = {
    '/home/viktor/GTARadio/GTA5/GTA3/CHAT.mp3': 300,  # replace 300 with actual duration in seconds
    '/home/viktor/GTARadio/GTA5/GTA3/CLASS.mp3': 250,
    '/home/viktor/GTARadio/GTA5/GTA3/FLASH.mp3': 320,
    '/home/viktor/GTARadio/GTA5/GTA3/GAME.mp3': 180,
    '/home/viktor/GTARadio/GTA5/GTA3/HEAD.mp3': 240,
    '/home/viktor/GTARadio/GTA5/GTA3/KJAH.mp3': 210,
    '/home/viktor/GTARadio/GTA5/GTA3/LIPS.mp3': 270,
    '/home/viktor/GTARadio/GTA5/GTA3/MSX.mp3': 260,
    '/home/viktor/GTARadio/GTA5/GTA3/RISE.mp3': 230
}

def play_radio_thread(selectedSong, duration):
    global mp3_process
    global stop_thread

    while not stop_thread:
        # Calculate a random starting point in seconds (as frames, where 1 frame = 1/75 second)
        random_start_frame = int(random.uniform(0, duration) * 75)

        print(f"Playing {selectedSong} from frame {random_start_frame}")

        # Start a new subprocess to play the selected MP3 file from a random point
        mp3_process = subprocess.Popen(['mpg123', '-k', str(random_start_frame), selectedSong])

        # Wait for the remaining duration minus a small buffer (e.g., 2 seconds)
        time.sleep(duration - (random_start_frame / 75) - 2)

        # Terminate the process
        if mp3_process and mp3_process.poll() is None:
            mp3_process.terminate()
            mp3_process.wait()

def play_radio(folder_index, image_index):
    global mp3_process
    global play_thread
    global stop_thread
    global selectedSong

    # Determine the song to play based on folder_index and image_index
    if folder_index == 0:
        if image_index == 1:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/CHAT.mp3'
        elif image_index == 2:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/CLASS.mp3'
        elif image_index == 3:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/FLASH.mp3'
        elif image_index == 4:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/GAME.mp3'
        elif image_index == 5:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/HEAD.mp3'
        elif image_index == 6:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/KJAH.mp3'
        elif image_index == 7:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/LIPS.mp3'
        elif image_index == 8:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/MSX.mp3'
        elif image_index == 9:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA3/RISE.mp3'
        else:
            return  # Handle unexpected image_index values

    # Terminate the existing MP3-playing subprocess, if any
    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

    # Stop the existing thread if it is running
    if play_thread and play_thread.is_alive():
        stop_thread = True
        play_thread.join()

    duration = mp3_durations.get(selectedSong)
    if duration is None:
        print("Error: Duration not found for selected song")
        return

    # Reset the stop_thread flag
    stop_thread = False

    # Start a new thread to play the selected MP3 file from a random point and loop it
    play_thread = threading.Thread(target=play_radio_thread, args=(selectedSong, duration))
    play_thread.start()

# Example usage:
# play_radio(0, 1)  # This would play CHAT.mp3 starting from a random point and loop it
# play_radio(0, 2)  # This would play CLASS.mp3 starting from a random point and loop it