import os

gamearray = ["GTA3", "GTAVC", "GTASA", "GTA4", "GTA5"]  # Sample game strings
GTA3array = ["CHAT", "CLASS", "FLASH", "GAME", "HEAD", "KJAH", "LIPS", "MSX", "RISE"]  # Sample channel strings
GTAVCarray = ["EMOTION", "ESPANT", "FEVER", "FLASH", "KCHAT", "VCPR", "WAVE", "WILD"]

current_game_index = 0
current_channel_index = 0

while True:
    key = input("Press 'a' for next game string, 'r' for next channel string: ").lower()

    if key == 'a':
        current_game_index = (current_game_index + 1) % len(gamearray)
        print("Game string:", gamearray[current_game_index])
    elif key == 'r':
        if current_game_index == 0:
            current_channel_index = (current_channel_index + 1) % len(GTA3array)
            print("Channel string:", GTA3array[current_channel_index])
        elif current_game_index == 1:
            current_channel_index = (current_channel_index + 1) % len(GTAVCarray)
            print("Channel string:", GTAVCarray[current_channel_index])

    elif key == 'l':
        if current_game_index == 0:
            current_channel_index = (current_channel_index - 1) % len(GTA3array)
            print("Channel string:", GTA3array[current_channel_index])
        elif current_game_index == 1:
            current_channel_index = (current_channel_index - 1) % len(GTAVCarray)
            print("Channel string:", GTAVCarray[current_channel_index])


    command = "vlc '/home/viktor/GTARadio/GTA5/{}/{}.mp3'".format(gamearray[current_game_index], GTA3array[current_channel_index])

    # Execute the command
    os.system(command)
