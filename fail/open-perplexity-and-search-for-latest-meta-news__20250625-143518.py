# Prompt: open perplexity and search for latest Meta news
# Outcome: fail

import requests

def get_meta_news():
    # Define the URL for the news source
    url = "https://api.currentsapi.services/v1/latest-news"
    api_key = "YOUR_API_KEY"  # Replace with your actual API key

    # Set up the parameters for the API request
    params = {
        'apiKey': api_key,
        'category': 'technology',  # Focus on technology news
        'keywords': 'Meta',
        'language': 'en'
    }

    try:
        # Make the request to the news API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        news_data = response.json()
        articles = news_data.get('news', [])

        # Print the titles and URLs of the latest articles
        if articles:
            for article in articles:
                title = article.get('title')
                url = article.get('url')
                print(f"Title: {title}\nURL: {url}\n")
        else:
            print("No articles found.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_meta_news()