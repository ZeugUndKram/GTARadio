import subprocess
import random

mp3_process = None

mp3_durations = {
    '/home/viktor/GTARadio/GTA5/GTA3/CHAT.mp3': 3484,
    '/home/viktor/GTARadio/GTA5/GTA3/CLASS.mp3': 1365,
    '/home/viktor/GTARadio/GTA5/GTA3/FLASH.mp3': 1125,
    '/home/viktor/GTARadio/GTA5/GTA3/GAME.mp3': 944,
    '/home/viktor/GTARadio/GTA5/GTA3/HEAD.mp3': 1405,
    '/home/viktor/GTARadio/GTA5/GTA3/KJAH.mp3': 1144,
    '/home/viktor/GTARadio/GTA5/GTA3/LIPS.mp3': 1206,
    '/home/viktor/GTARadio/GTA5/GTA3/MSX.mp3': 1500,
    '/home/viktor/GTARadio/GTA5/GTA3/RISE.mp3': 1568,
    '/home/viktor/GTARadio/GTA5/GTAVC/EMOTION.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/ESPANT.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/FEVER.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/FLASH.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/KCHAT.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/VCPR.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/VROCK.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/WAVE.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTAVC/WILD.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/Bounce FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/CSR 103.9.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/K-DST.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/K-JAH West.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/K-Rose.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/Master Sounds 98.3.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/Playback FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/Radio Los Santos.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/Radio X.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/SF-UR.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTASA/West Coast Talk Radio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Electro-Choc.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/K109 The Studio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Massive B Soundsystem 96.9.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/RamJam FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/The Beat 102.7.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/The Vibe 98.8.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Vladivostok FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Integrity 2.0.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Liberty City Hardcore.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Public Liberty Radio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/San Juan Sounds.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/The Classics 104.1.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Tuff Gong Radio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/WKTT Radio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Jazz Nation Radio 108.5.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Liberty Rock Radio.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Radio Broker.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Self-Actualization FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/The Journey.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA4/Vice City FM.mp3': 300,
    '/home/viktor/GTARadio/GTA5/GTA5/Blaine County Radio.mp3': 4891,
    '/home/viktor/GTARadio/GTA5/GTA5/Channel X.mp3': 2827,
    '/home/viktor/GTARadio/GTA5/GTA5/Los Santos Rock Radio.mp3': 9322,
    '/home/viktor/GTARadio/GTA5/GTA5/Radio Los Santos.mp3': 6691,
    '/home/viktor/GTARadio/GTA5/GTA5/Soulwax FM.mp3': 2566,
    '/home/viktor/GTARadio/GTA5/GTA5/The Lowdown 91.1.mp3': 4372,
    '/home/viktor/GTARadio/GTA5/GTA5/West Coast Talk Radio.mp3': 5617,
    '/home/viktor/GTARadio/GTA5/GTA5/Blonded Radio.mp3': 6139,
    '/home/viktor/GTARadio/GTA5/GTA5/East Los FM.mp3': 2465,
    '/home/viktor/GTARadio/GTA5/GTA5/Los Santos Underground Radio.mp3': 16730,
    '/home/viktor/GTARadio/GTA5/GTA5/Radio Mirror Park.mp3': 9160,
    '/home/viktor/GTARadio/GTA5/GTA5/Space 103.2.mp3': 5653,
    '/home/viktor/GTARadio/GTA5/GTA5/Vinewood Boulevard Radio.mp3': 3957,
    '/home/viktor/GTARadio/GTA5/GTA5/WorldWide FM.mp3': 7232,
    '/home/viktor/GTARadio/GTA5/GTA5/Blue Ark.mp3': 4790,
    '/home/viktor/GTARadio/GTA5/GTA5/FlyLo FM.mp3': 4298,
    '/home/viktor/GTARadio/GTA5/GTA5/Non-Stop-Pop FM.mp3': 10005,
    '/home/viktor/GTARadio/GTA5/GTA5/Rebel Radio.mp3': 3457,
    '/home/viktor/GTARadio/GTA5/GTA5/The Lab.mp3': 3455,
    '/home/viktor/GTARadio/GTA5/GTA5/West Coast Classics.mp3': 6977
}

def play_radio(folder_index, image_index):
    global mp3_process
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
    if folder_index == 1:
        if image_index == 1:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/EMOTION.mp3'
        elif image_index == 2:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/ESPANT.mp3'
        elif image_index == 3:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/FEVER.mp3'
        elif image_index == 4:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/FLASH.mp3'
        elif image_index == 5:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/KCHAT.mp3'
        elif image_index == 6:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/VCPR.mp3'
        elif image_index == 7:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/VROCK.mp3'
        elif image_index == 8:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/WAVE.mp3'
        elif image_index == 9:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTAVC/WILD.mp3'
    if folder_index == 2:
        if image_index == 1:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/Bounce FM.mp3'
        elif image_index == 2:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/CSR 103.9.mp3'
        elif image_index == 3:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/K-DST.mp3'
        elif image_index == 4:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/K-JAH West.mp3'
        elif image_index == 5:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/K-Rose.mp3'
        elif image_index == 6:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/Master Sounds 98.3.mp3'
        elif image_index == 7:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/Playback FM.mp3'
        elif image_index == 8:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/Radio Los Santos.mp3'
        elif image_index == 9:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/Radio X.mp3'
        elif image_index == 10:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/SF-UR.mp3'
        elif image_index == 11:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTASA/West Coast Talk Radio.mp3'
    elif folder_index == 3:
        if image_index == 1:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Electro-Choc.mp3'
        elif image_index == 2:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Integrity 2.0.mp3'
        elif image_index == 3:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Jazz Nation Radio 108.5.mp3'
        elif image_index == 4:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/K109 The Studio.mp3'
        elif image_index == 5:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Liberty City Hardcore.mp3'
        elif image_index == 6:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Liberty Rock Radio.mp3'
        elif image_index == 7:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Massive B Soundsystem 96.9.mp3'
        elif image_index == 8:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Public Liberty Radio.mp3'
        elif image_index == 9:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Radio Broker.mp3'
        elif image_index == 10:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/RamJam FM.mp3'
        elif image_index == 11:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/San Juan Sounds.mp3'
        elif image_index == 12:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Self-Actualization FM.mp3'
        elif image_index == 13:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/The Beat 102.7.mp3'
        elif image_index == 14:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/The Classics 104.1.mp3'
        elif image_index == 15:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/The Journey.mp3'
        elif image_index == 16:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/The Vibe 98.8.mp3'
        elif image_index == 17:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Tuff Gong Radio.mp3'
        elif image_index == 18:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Vice City FM.mp3'
        elif image_index == 19:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/Vladivostok FM.mp3'
        elif image_index == 20:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA4/WKTT Radio.mp3'
    elif folder_index == 4:
        if image_index == 1:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Blaine County Radio.mp3'
        elif image_index == 2:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Blonded Radio.mp3'
        elif image_index == 3:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Channel X.mp3'
        elif image_index == 4:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/East Los FM.mp3'
        elif image_index == 5:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/FlyLo FM.mp3'
        elif image_index == 6:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Los Santos Rock Radio.mp3'
        elif image_index == 7:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Non-Stop-Pop FM.mp3'
        elif image_index == 8:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Radio Mirror Park.mp3'
        elif image_index == 9:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Rebel Radio.mp3'
        elif image_index == 10:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Space 103.2.mp3'
        elif image_index == 11:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Soulwax FM.mp3'
        elif image_index == 12:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Blue Ark.mp3'
        elif image_index == 13:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/The Lab.mp3'
        elif image_index == 14:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/The Lowdown 91.1.mp3'
        elif image_index == 15:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/Vinewood Boulevard Radio.mp3'
        elif image_index == 16:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/West Coast Talk Radio.mp3'
        elif image_index == 17:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/West Coast Classics.mp3'
        elif image_index == 18:
            selectedSong = '/home/viktor/GTARadio/GTA5/GTA5/WorldWide FM.mp3'

        else:
            return  # Handle unexpected image_index values

    # Terminate the existing MP3-playing subprocess, if any
    if mp3_process and mp3_process.poll() is None:
        mp3_process.terminate()
        mp3_process.wait()

    # Get the duration of the selected MP3 file from the dictionary
    duration = mp3_durations.get(selectedSong)
    if duration is None:
        print("Error: Duration not found for selected song")
        return

    # Calculate a random starting point in seconds (as frames, where 1 frame = 1/75 second)
    random_start_frame = int(random.uniform(0, duration) * 75)

    print(f"Playing {selectedSong} from frame {random_start_frame}")

    # Start a new subprocess to play the selected MP3 file from a random point
    mp3_process = subprocess.Popen(['mpg123', '-k', str(random_start_frame), '-l', '0', selectedSong])
