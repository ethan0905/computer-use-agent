# Prompt: open perplexity and search for latest news
# Outcome: fail

import webbrowser

def open_perplexity_and_search(query):
    # Construct the search URL for perplexity.ai
    base_url = "https://www.perplexity.ai/search?q="
    search_url = base_url + query.replace(" ", "%20")
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    # Search for the latest news about OpenAI
    open_perplexity_and_search("OpenAI latest news")