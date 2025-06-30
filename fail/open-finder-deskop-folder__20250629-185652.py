# Prompt: open finder deskop folder
# Outcome: fail

import subprocess

def open_finder_desktop():
    try:
        subprocess.run(["open", "~/Desktop"])
        print("Opened Desktop folder in Finder.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_finder_desktop()