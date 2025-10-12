import time

def call_after_five_seconds():
    print("5 seconds have passed!")

# Get the current time
start_time = time.time()

# Continuously check if 5 seconds have passed
while True:
    current_time = time.time()
    if current_time - start_time >= 5:
        call_after_five_seconds()
        break
