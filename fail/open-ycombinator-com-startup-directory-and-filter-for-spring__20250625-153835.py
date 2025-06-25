# Prompt: open ycombinator.com startup directory and filter for Spring 2025 batch
# Outcome: fail

import webbrowser
import subprocess
import time

def open_ycombinator_and_filter(spring_year):
    # Open the Y Combinator startup directory
    url = "https://www.ycombinator.com/companies"
    webbrowser.open(url)

    # AppleScript to filter for Spring 2025
    applescript = f'''
    tell application "System Events"
        set browserName to "Safari" -- Change to your browser if needed
        if application browserName is running then
            tell application browserName
                activate
            end tell
            
            delay 1 -- Allow the browser to become active

            tell process browserName
                set frontmost to true
                try
                    -- Check if the window is available
                    if (count of windows) > 0 then
                        set theWindow to front window
                        set theURL to URL of theWindow
                        if theURL is "{url}" then
                            -- Open the find dialog and type the search term
                            keystroke "f" using command down
                            delay 0.5
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
        else
            display dialog "The specified browser is not running."
        end if
    end tell
    '''

    # Execute the AppleScript
    subprocess.run(['osascript', '-e', applescript])

if __name__ == "__main__":
    open_ycombinator_and_filter(2025)