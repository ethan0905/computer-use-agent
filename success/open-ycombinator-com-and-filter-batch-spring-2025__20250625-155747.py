# Prompt: open ycombinator.com and filter batch: Spring 2025
# Outcome: success

import webbrowser
import subprocess
import time

def open_ycombinator_and_filter(spring_year):
    # Define the URL for Y Combinator
    url = "https://www.ycombinator.com/companies"

    # Open the Y Combinator startup directory in the default web browser
    webbrowser.open(url)

    # AppleScript to filter for Spring 2025 batch
    applescript = f'''
    tell application "System Events"
        set browserName to "Safari" -- Change to your preferred browser if needed
        if application browserName is running then
            tell application browserName
                activate
            end tell

            tell process browserName
                set frontmost to true
                try
                    -- Wait for the window to be available
                    repeat until (count of windows) > 0
                        delay 0.1
                    end repeat

                    set theWindow to front window
                    set theURL to URL of theWindow

                    if theURL contains "{url}" then
                        -- Open the find dialog and type the search term
                        keystroke "f" using command down
                        delay 0.1
                        keystroke "Spring {spring_year}"
                        delay 0.1
                        keystroke return
                    else
                        display dialog "The Y Combinator page is not open."
                    end if
                on error errMsg
                    display dialog "An error occurred: " & errMsg
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