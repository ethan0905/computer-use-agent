# Prompt: search for OpenAI latest news on perplexity.ai
# Outcome: fail

import requests
from bs4 import BeautifulSoup

def fetch_openai_news():
    url = "https://www.perplexity.ai/search?q=openai"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')  # Adjust the selector based on the actual HTML structure
        
        news_items = []
        for article in articles:
            title = article.find('h2')  # Adjust based on actual HTML structure
            link = article.find('a', href=True)
            if title and link:
                news_items.append({
                    'title': title.get_text(),
                    'link': link['href']
                })
        
        return news_items
    else:
        print("Failed to retrieve news")
        return []

if __name__ == "__main__":
    news = fetch_openai_news()
    for item in news:
        print(f"Title: {item['title']}\nLink: {item['link']}\n")