# Prompt: open perplexity and search for latest OpenAI news
# Outcome: success

import webbrowser

def search_openai_news():
    # Construct the search URL for Perplexity with the query for OpenAI news
    query = "OpenAI latest news"
    base_url = "https://www.perplexity.ai/search?q="
    search_url = base_url + query.replace(" ", "%20")

    # Open the constructed URL in the default web browser
    webbrowser.open(search_url)

if __name__ == "__main__":
    search_openai_news()