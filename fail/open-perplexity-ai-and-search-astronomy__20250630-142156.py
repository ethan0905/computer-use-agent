# Prompt: open perplexity.ai and search astronomy
# Outcome: fail

import webbrowser
import time

def open_website_and_search(url, query):
    try:
        # Open the website
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
        
        # Wait for the browser to load the page
        time.sleep(5)  # Adjust this if necessary based on your internet speed
        
        # Construct the search URL
        search_url = f"{url}/search?q={query}"
        webbrowser.open(search_url)
        print(f"Searching for '{query}' on {url}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_website_and_search("https://www.perplexity.ai", "astronomy")