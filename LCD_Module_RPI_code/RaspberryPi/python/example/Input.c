#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>

int main() {
    // Open the input event device
    int fd = open("/dev/input/event0", O_WRONLY);
    if (fd == -1) {
        perror("Error opening input device");
        return 1;
    }

    // Simulate pressing the 'a' key
    struct input_event event;
    event.type = EV_KEY;
    event.code = KEY_A;
    event.value = 1; // Press the key
    if (write(fd, &event, sizeof(event)) == -1) {
        perror("Error writing key press event");
        close(fd);
        return 1;
    }

    // Simulate releasing the 'a' key
    event.value = 0; // Release the key
    if (write(fd, &event, sizeof(event)) == -1) {
        perror("Error writing key release event");
        close(fd);
        return 1;
    }

    // Close the device
    close(fd);

    return 0;
}
