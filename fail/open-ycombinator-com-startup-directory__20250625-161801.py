# Prompt: open ycombinator.com startup directory
# Outcome: fail

import webbrowser
import time

def search_ycombinator(query):
    try:
        url = f"https://www.ycombinator.com/search?query={query}"
        webbrowser.open(url)
        print(f"Opened search results for '{query}' on Y Combinator.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_ycombinator("startup directory")