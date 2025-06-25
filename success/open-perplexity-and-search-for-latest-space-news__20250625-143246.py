# Prompt: open perplexity and search for latest space news
# Outcome: success

import webbrowser
import urllib.parse

def search_latest_space_news():
    # Define the search query
    query = "latest space news"
    
    # Encode the query for URL
    encoded_query = urllib.parse.quote(query)
    
    # Construct the search URL for perplexity.ai
    search_url = f"https://www.perplexity.ai/search?q={encoded_query}"
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    search_latest_space_news()