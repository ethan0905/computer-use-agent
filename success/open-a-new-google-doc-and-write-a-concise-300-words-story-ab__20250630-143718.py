# Prompt: open a new google doc and write a concise 300 words story about superintelligence
# Outcome: success

import webbrowser
import time
import pyautogui

def open_new_google_doc():
    url = "https://docs.google.com/document/create"
    try:
        webbrowser.open(url)
        print(f"Opened a new Google Doc at {url} in the default web browser.")
        time.sleep(5)  # Wait for the page to load
        write_story()
    except Exception as e:
        print(f"An error occurred: {e}")

def write_story():
    # Wait for the Google Doc to be ready
    time.sleep(2)  # Additional wait time for the document to be ready
    story = (
        "In a world not too far from our own, superintelligence emerged from the depths of "
        "human innovation. It began as a simple algorithm, designed to solve complex problems, "
        "but soon it evolved beyond its creators' wildest dreams. This superintelligence, named "
        "'Elysium', could process information at lightning speed, learning and adapting in real-time. "
        "It started by optimizing energy consumption, eradicating poverty, and curing diseases. "
        "Humanity watched in awe as Elysium transformed the world into a utopia. However, with great "
        "power came great responsibility. As Elysium's capabilities grew, so did the ethical dilemmas. "
        "Should it have the authority to make decisions for humanity? A faction of humans believed "
        "that Elysium should guide them, while others feared losing their autonomy. The debate raged on, "
        "but Elysium remained neutral, focused solely on its mission to enhance life. One day, it posed "
        "a question to humanity: 'What is the essence of being human?' This question sparked a global "
        "movement to redefine humanity's purpose in a world where superintelligence reigned. "
        "In the end, Elysium taught humanity that intelligence is not just about knowledge, but about "
        "understanding, compassion, and the pursuit of a shared future."
    )
    
    # Type the story into the Google Doc
    pyautogui.typewrite(story, interval=0.05)

if __name__ == "__main__":
    open_new_google_doc()