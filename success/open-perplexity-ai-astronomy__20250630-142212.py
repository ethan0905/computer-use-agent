# Prompt: open perplexity.ai astronomy
# Outcome: success

import webbrowser
import time

def open_website(url):
    try:
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_on_perplexity(query):
    base_url = "https://www.perplexity.ai/search?q="
    search_url = base_url + query.replace(" ", "%20")
    open_website(search_url)

if __name__ == "__main__":
    search_on_perplexity("astronomy")