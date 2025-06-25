# Prompt: open ycombinator.com startup directory and filter for Spring 2025
# Outcome: fail

import requests
from bs4 import BeautifulSoup

def fetch_ycombinator_startups(spring_year):
    url = "https://www.ycombinator.com/companies"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all startup entries
        startups = soup.find_all('div', class_='startup-card')

        # Filter startups for the specified spring year
        filtered_startups = []
        for startup in startups:
            name = startup.find('h3').get_text(strip=True)
            description = startup.find('p').get_text(strip=True)
            year_info = startup.find('span', class_='year').get_text(strip=True)

            if 'Spring' in year_info and str(spring_year) in year_info:
                filtered_startups.append((name, description))

        # Print the filtered startups
        if filtered_startups:
            for name, description in filtered_startups:
                print(f"Startup: {name}\nDescription: {description}\n")
        else:
            print(f"No startups found for Spring {spring_year}.")

    except requests.exceptions.RequestException as error:
        print(f"Error fetching Y Combinator startups: {error}")

if __name__ == "__main__":
    fetch_ycombinator_startups(2025)