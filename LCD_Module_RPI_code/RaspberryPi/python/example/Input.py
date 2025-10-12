import subprocess

def press_key():
    try:
        subprocess.run(["./InputC"])  # Run the C program
    except FileNotFoundError:
        print("Error: press_key program not found.")

# Call the press_key function
press_key()
