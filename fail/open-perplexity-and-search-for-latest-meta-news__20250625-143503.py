# Prompt: open perplexity and search for latest Meta news
# Outcome: fail

import requests
from bs4 import BeautifulSoup

def search_meta_news():
    # Define the search URL for Perplexity
    search_url = "https://www.perplexity.ai/search?q=Meta+latest+news"

    try:
        # Send a GET request to the search URL
        response = requests.get(search_url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and print the titles and links of the news articles
        articles = soup.find_all('article')  # Adjust the selector based on the actual structure
        if articles:
            for article in articles:
                title = article.find('h2').get_text() if article.find('h2') else 'No title'
                link = article.find('a')['href'] if article.find('a') else 'No link'
                print(f"Title: {title}\nURL: {link}\n")
        else:
            print("No articles found.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_meta_news()