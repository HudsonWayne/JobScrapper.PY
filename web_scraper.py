import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "https://vacancymail.co.zw/jobs/"
csv_file = "scraped_data.csv"

def scrape_jobs():
    try:
        logging.info("Started scraping...")
        response = requests.get(URL)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Debug: Print out the first 1000 characters of the response content to check if it's correct
            logging.debug(f"Response content (first 1000 characters): {response.text[:1000]}")

            # Print prettified HTML to check the structure (first 1000 characters)
            logging.debug(f"Soup: {soup.prettify()[:1000]}")  # First 1000 chars of prettified HTML for debugging

            # Look for the correct div elements that contain the job cards
            job_cards = soup.find_all('div', class_='job-title', limit=10)

            if not job_cards:
                logging.error("No job cards found.")
            else:
                logging.debug(f"Found {len(job_cards)} job cards.")

            data = []

            for card in job_cards:
                title = card.text.strip()
                parent = card.find_parent('div', class_='card-body')
                company = parent.find('h6').text.strip() if parent.find('h6') else "N/A"
                location = parent.find('span', class_='location').text.strip() if parent.find('span', class_='location') else "N/A"
                expiry = parent.find('span', class_='text-danger').text.strip() if parent.find('span', class_='text-danger') else "N/A"
                link = "https://vacancymail.co.zw" + card.find('a')['href']

                # Debug: Log each job data fetched
                logging.debug(f"Job Title: {title}, Company: {company}, Location: {location}, Expiry: {expiry}, Link: {link}")

                job_response = requests.get(link)
                job_soup = BeautifulSoup(job_response.text, 'html.parser')
                desc_section = job_soup.find('div', class_='card-body')
                description = desc_section.text.strip() if desc_section else "N/A"

                # Log the description as well for debugging
                logging.debug(f"Description: {description}")

                data.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Expiry Date': expiry,
                    'Description': description
                })

            # Log the final data being added
            logging.debug(f"Data extracted: {data}")

            # Create DataFrame and drop duplicates
            df = pd.DataFrame(data)

            # Check if the file exists
            if os.path.exists(csv_file):
                try:
                    # Read the existing file and append the new data
                    existing_df = pd.read_csv(csv_file)
                    combined_df = pd.concat([existing_df, df])
                    combined_df.drop_duplicates(inplace=True)
                    combined_df.to_csv(csv_file, index=False)
                    logging.info("Data appended to existing file.")
                except pd.errors.EmptyDataError:
                    # In case the file is empty, create a new one
                    df.to_csv(csv_file, index=False)
                    logging.info("New file created and data saved.")
            else:
                # If the file doesn't exist, create a new one
                df.to_csv(csv_file, index=False)
                logging.info("New file created and data saved.")

        else:
            logging.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

def schedule_scraping():
    schedule.every(30).seconds.do(scrape_jobs)
    print("Scraper is running every 30 seconds... Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_scraping()



