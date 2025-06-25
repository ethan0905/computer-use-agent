# Prompt: open perplexity and search for latest news
# Outcome: fail

import webbrowser
import time

def search_perplexity(query):
    # Construct the search URL for perplexity.ai
    base_url = "https://www.perplexity.ai/search?q="
    search_url = base_url + query.replace(" ", "%20")
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    # Wait a moment to ensure the browser is ready
    time.sleep(1)
    search_perplexity("OpenAI latest news")