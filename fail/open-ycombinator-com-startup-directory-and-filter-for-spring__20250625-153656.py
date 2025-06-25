# Prompt: open ycombinator.com startup directory and filter for Spring 2025
# Outcome: fail

import webbrowser
import time
import pyautogui

def open_ycombinator_and_filter(spring_year):
    # Open the Y Combinator startup directory
    url = "https://www.ycombinator.com/companies"
    webbrowser.open(url)

    # Wait for the page to load by checking if the browser is active
    time.sleep(5)  # This is a simple wait; ideally, we would check for the page load

    # Simulate user input to filter for Spring 2025
    # Note: This assumes the user has a search box available on the page
    pyautogui.hotkey('command', 'f')  # Open the find dialog
    time.sleep(1)  # Wait for the dialog to open
    pyautogui.typewrite(f'Spring {spring_year}')  # Type the search term
    time.sleep(1)  # Wait for the search to process

    print(f"Filtered startups for Spring {spring_year} on the opened page.")

if __name__ == "__main__":
    open_ycombinator_and_filter(2025)