# Prompt: open ycombinator.com and search for startup directory, filter Spring 2025 batch, filter companies in robotic
# Outcome: fail

import webbrowser

def open_website(url):
    try:
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_ycombinator(query, filter_batch, filter_category):
    base_url = "https://www.ycombinator.com/companies"
    search_url = f"{base_url}?search={query}&batch={filter_batch}&category={filter_category}"
    open_website(search_url)

if __name__ == "__main__":
    search_ycombinator("startup directory", "Spring 2025", "robotic")