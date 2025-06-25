# Prompt: open perplexity and search for latest AI news
# Outcome: success

import webbrowser

def search_latest_ai_news():
    # Define the search query for the latest AI news
    query = "latest AI news"
    
    # Construct the search URL for perplexity.ai
    search_url = f"https://www.perplexity.ai/search?q={query.replace(' ', '%20')}"
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    search_latest_ai_news()