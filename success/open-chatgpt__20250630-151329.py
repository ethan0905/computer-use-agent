# Prompt: open chatgpt
# Outcome: success

import webbrowser

def open_chatgpt():
    url = "https://chat.openai.com/"
    try:
        webbrowser.open(url)
        print(f"Opened {url} in the default web browser.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_chatgpt()