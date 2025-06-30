# Prompt: open perplexity astronomy
# Outcome: success

import webbrowser

def open_perplexity_with_query(query):
    base_url = "https://www.perplexity.ai/search?q="
    search_url = base_url + query.replace(" ", "%20")
    try:
        webbrowser.open(search_url)
        print(f"Opened {search_url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_perplexity_with_query("astronomy")