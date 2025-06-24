import os
import time

# Open Safari
os.system("open -a Safari")

# Wait for Safari to open
time.sleep(2)

# Open the specified URL
os.system("osascript -e 'tell application \"Safari\" to open location \"https://www.ycombinator.com\"'")