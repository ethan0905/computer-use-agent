# Prompt: open ycombinator.com startup directory
# Outcome: success

import webbrowser

def open_y_combinator_startup_directory():
    url = "https://www.ycombinator.com/companies"
    webbrowser.open(url)

if __name__ == "__main__":
    open_y_combinator_startup_directory()