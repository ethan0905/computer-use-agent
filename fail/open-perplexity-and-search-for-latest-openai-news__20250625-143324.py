# Prompt: open perplexity and search for latest OpenAI news
# Outcome: fail

import requests
from bs4 import BeautifulSoup

def fetch_openai_news():
    # Define the URL for the Perplexity search
    search_url = "https://www.perplexity.ai/search?q=OpenAI%20latest%20news"
    
    # Send a GET request to the search URL
    response = requests.get(search_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find and print the titles of the news articles
        for item in soup.find_all('h2'):
            print(item.get_text())
    else:
        print("Failed to retrieve news.")

if __name__ == "__main__":
    fetch_openai_news()