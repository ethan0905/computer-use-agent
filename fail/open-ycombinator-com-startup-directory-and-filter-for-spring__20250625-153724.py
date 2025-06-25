# Prompt: open ycombinator.com startup directory and filter for Spring 2025 batch
# Outcome: fail

import webbrowser
import time
import subprocess

def open_ycombinator_and_filter(spring_year):
    # Open the Y Combinator startup directory
    url = "https://www.ycombinator.com/companies"
    webbrowser.open(url)

    # Wait for the browser to open and load the page
    time.sleep(5)  # This is a simple wait; ideally, we would check for the page load

    # Use AppleScript to filter for Spring 2025
    applescript = f'''
    tell application "System Events"
        tell process "Safari" -- Change to your browser if needed
            set frontmost to true
            delay 1
            try
                -- Check if the window is available
                if (count of windows) > 0 then
                    set theWindow to front window
                    set theURL to URL of theWindow
                    if theURL is "{url}" then
                        -- Simulate typing in the search box
                        keystroke "f" using {command down}
                        delay 1
                        keystroke "Spring {spring_year}"
                    else
                        display dialog "The Y Combinator page is not open."
                    end if
                else
                    display dialog "No windows are open."
                end if
            on error
                display dialog "An error occurred while trying to filter."
            end try
        end tell
    end tell
    '''

    # Execute the AppleScript
    subprocess.run(['osascript', '-e', applescript])

if __name__ == "__main__":
    open_ycombinator_and_filter(2025)