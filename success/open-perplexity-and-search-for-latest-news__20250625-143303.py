# Prompt: open perplexity and search for latest news
# Outcome: success

import webbrowser
import urllib.parse

def search_latest_news_on_perplexity():
    # Define the search query
    query = "latest news"
    
    # Encode the query for the URL
    encoded_query = urllib.parse.quote(query)
    
    # Construct the search URL for perplexity.ai
    search_url = f"https://www.perplexity.ai/search?q={encoded_query}"
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    search_latest_news_on_perplexity()