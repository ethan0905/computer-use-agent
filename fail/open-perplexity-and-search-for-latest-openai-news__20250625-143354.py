# Prompt: open perplexity and search for latest OpenAI news
# Outcome: fail

import requests

def get_latest_openai_news():
    # Define the API endpoint for fetching news
    api_url = "https://newsapi.org/v2/everything"
    api_key = "YOUR_API_KEY"  # Replace with your actual News API key

    # Set up the parameters for the API request
    params = {
        'q': 'OpenAI',
        'sortBy': 'publishedAt',
        'apiKey': api_key,
        'pageSize': 5  # Limit to the latest 5 articles
    }

    # Make the request to the News API
    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
        
        # Print the titles and URLs of the latest articles
        for article in articles:
            title = article.get('title')
            url = article.get('url')
            print(f"Title: {title}\nURL: {url}\n")
    else:
        print("Failed to retrieve news.")

if __name__ == "__main__":
    get_latest_openai_news()