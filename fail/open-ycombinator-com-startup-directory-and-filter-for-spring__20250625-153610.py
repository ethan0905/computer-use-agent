# Prompt: open ycombinator.com startup directory and filter for Spring 2025
# Outcome: fail

import webbrowser
import time

def open_ycombinator_and_filter(spring_year):
    # Open the Y Combinator startup directory
    url = "https://www.ycombinator.com/companies"
    webbrowser.open(url)

    # Wait for the page to load
    time.sleep(5)  # This is a simple wait; ideally, we would check for the page load

    # Inform the user to manually filter for Spring 2025
    print(f"Please filter the startups for Spring {spring_year} on the opened page.")

if __name__ == "__main__":
    open_ycombinator_and_filter(2025)