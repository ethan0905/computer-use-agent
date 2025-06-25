# Prompt: open perplexity and search for latest Meta news
# Outcome: fail

import requests

def fetch_latest_meta_news():
    # Define the endpoint for fetching news
    endpoint = "https://newsapi.org/v2/everything"
    api_key = "YOUR_API_KEY"  # Replace with your actual News API key

    # Set up the parameters for the API request
    params = {
        'q': 'Meta',
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'publishedAt',  # Sort by latest published articles
        'pageSize': 5  # Limit to the latest 5 articles
    }

    try:
        # Make the request to the news API
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        news_data = response.json()
        articles = news_data.get('articles', [])

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
    fetch_latest_meta_news()