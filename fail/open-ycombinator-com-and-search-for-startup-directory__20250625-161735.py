# Prompt: open ycombinator.com and search for startup directory
# Outcome: fail

import webbrowser
import time

def open_website_and_search(url, search_query):
    try:
        # Open the website
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
        
        # Wait for the browser to open
        time.sleep(2)  # Adjust if necessary based on your system's speed
        
        # Construct the search URL
        search_url = f"{url}/search?query={search_query.replace(' ', '+')}"
        
        # Open the search URL
        webbrowser.open(search_url)
        print(f"Searched for '{search_query}' on {url}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_website_and_search("https://www.ycombinator.com", "startup directory")