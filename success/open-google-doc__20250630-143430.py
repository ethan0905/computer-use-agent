# Prompt: open google doc
# Outcome: success

import webbrowser

def open_google_doc():
    url = "https://docs.google.com/document/"
    try:
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_google_doc()