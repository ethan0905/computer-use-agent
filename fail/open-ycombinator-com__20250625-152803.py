# Prompt: open ycombinator.com
# Outcome: fail

import requests

def get_latest_meta_news():
    # Define the API endpoint for fetching news
    api_url = "https://newsapi.org/v2/everything"
    api_key = "YOUR_API_KEY"  # Replace with your actual News API key

    # Parameters for the API request
    query_params = {
        'q': 'Meta',
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5
    }

    try:
        # Send a GET request to the news API
        response = requests.get(api_url, params=query_params)
        response.raise_for_status()  # Check for HTTP errors

        # Extract articles from the response
        articles = response.json().get('articles', [])

        # Display the latest articles
        if articles:
            for article in articles:
                title = article.get('title', 'No Title')
                link = article.get('url', 'No URL')
                print(f"Title: {title}\nLink: {link}\n")
        else:
            print("No articles found.")

    except requests.exceptions.RequestException as error:
        print(f"Error fetching news: {error}")

if __name__ == "__main__":
    get_latest_meta_news()