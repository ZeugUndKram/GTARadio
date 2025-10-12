#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

void playSong(char* filename) {
    char command[256];
    sprintf(command, "cvlc --play-and-exit \"%s\"", filename);
    system(command);
}

int main() {
    DIR *dir;
    struct dirent *ent;
    char songsFolder[] = "/home/viktor/GTARadio/GTA5/GTA3";
    char songs[100][256];
    int count = 0;

    if ((dir = opendir(songsFolder)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (strcmp(ent->d_name, ".") != 0 && strcmp(ent->d_name, "..") != 0) {
                strcpy(songs[count], ent->d_name);
                count++;
            }
        }
        closedir(dir);
    } else {
        perror("Error opening directory");
        return EXIT_FAILURE;
    }

    if (count == 0) {
        printf("No songs found in the 'songs' directory.\n");
        return EXIT_SUCCESS;
    }

    int currentSongIndex = 0;
    char input;
    while (1) {
        printf("Press 'r' to play the next song, 'l' to play the previous song, or 'q' to quit: ");
        scanf(" %c", &input);
        if (input == 'r') {
            currentSongIndex = (currentSongIndex + 1) % count;
            playSong(songs[currentSongIndex]);
        } else if (input == 'l') {
            currentSongIndex = (currentSongIndex - 1 + count) % count;
            playSong(songs[currentSongIndex]);
        } else if (input == 'q') {
            printf("Exiting...\n");
            break;
        } else {
            printf("Invalid input. Press 'r' to play the next song, 'l' to play the previous song, or 'q' to quit.\n");
        }
    }

    return EXIT_SUCCESS;
}
