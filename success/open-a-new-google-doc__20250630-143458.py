# Prompt: open a new google doc
# Outcome: success

import webbrowser

def open_new_google_doc():
    url = "https://docs.google.com/document/create"
    try:
        webbrowser.open(url)
        print(f"Opened a new Google Doc at {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_new_google_doc()