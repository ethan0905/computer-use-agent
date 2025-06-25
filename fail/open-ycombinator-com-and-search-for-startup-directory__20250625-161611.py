# Prompt: open ycombinator.com and search for startup directory
# Outcome: fail

import webbrowser
import time
import urllib.parse

def open_website(url):
    try:
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_ycombinator(query):
    base_url = "https://www.ycombinator.com"
    search_url = f"{base_url}/search?query={urllib.parse.quote(query)}"
    open_website(search_url)

if __name__ == "__main__":
    open_website("https://www.ycombinator.com")
    time.sleep(2)  # Wait for the page to load
    search_ycombinator("startup directory")