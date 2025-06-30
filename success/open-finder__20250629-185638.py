# Prompt: open finder
# Outcome: success

import subprocess

def open_finder():
    try:
        subprocess.run(["open", "-a", "Finder"])
        print("Opened Finder.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_finder()