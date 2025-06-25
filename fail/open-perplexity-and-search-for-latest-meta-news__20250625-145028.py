# Prompt: open perplexity and search for latest Meta news
# Outcome: fail

import requests

def search_latest_meta_news():
    # Define the URL for the news API
    url = "https://newsapi.org/v2/everything"
    api_key = "YOUR_API_KEY"  # Replace with your actual News API key

    # Set up the parameters for the API request
    params = {
        'q': 'Meta',
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5
    }

    try:
        # Make the request to the news API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        news_data = response.json()
        articles = news_data.get('articles', [])

        # Check if articles are found and print them
        if articles:
            for article in articles:
                title = article.get('title', 'No Title Available')
                url = article.get('url', 'No URL Available')
                published_at = article.get('publishedAt', 'No Date Available')
                print(f"Title: {title}\nURL: {url}\nPublished At: {published_at}\n")
        else:
            print("No articles found.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_latest_meta_news()