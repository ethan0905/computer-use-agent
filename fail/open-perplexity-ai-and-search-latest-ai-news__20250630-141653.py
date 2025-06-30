# Prompt: open perplexity.ai and search latest ai news
# Outcome: fail

import webbrowser
import time

def open_website_and_search(url, search_query):
    try:
        # Open the website
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
        
        # Wait for the page to load
        time.sleep(5)  # Adjust this if necessary based on your internet speed
        
        # Construct the search URL
        search_url = f"{url}/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(search_url)
        print(f"Searched for '{search_query}' on {url}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_website_and_search("https://www.perplexity.ai", "latest ai news")