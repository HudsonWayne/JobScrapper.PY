import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import logging
from datetime import datetime
import os

# Logging setup
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

URL = "https://vacancymail.co.zw/jobs/"

def scrape_jobs():
    try:
        logging.info("Started scraping")
        response = requests.get(URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='job-title', limit=10)

        data = []

        for card in job_cards:
            title = card.text.strip()
            parent = card.find_parent('div', class_='card-body')
            company = parent.find('h6').text.strip() if parent.find('h6') else "N/A"
            location = parent.find('span', class_='location').text.strip() if parent.find('span', class_='location') else "N/A"
            expiry = parent.find('span', class_='text-danger').text.strip() if parent.find('span', class_='text-danger') else "N/A"
            link = "https://vacancymail.co.zw" + card.find('a')['href']

            # Get job description from job detail page
            job_response = requests.get(link)
            job_soup = BeautifulSoup(job_response.text, 'html.parser')
            desc_section = job_soup.find('div', class_='card-body')
            description = desc_section.text.strip() if desc_section else "N/A"

            data.append({
                'Title': title,
                'Company': company,
                'Location': location,
                'Expiry Date': expiry,
                'Description': description
            })

        df = pd.DataFrame(data)
        df.drop_duplicates(inplace=True)

        csv_file = "scraped_data.csv"

        # Append data or create file if it doesn't exist
        if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df])
            combined_df.drop_duplicates(inplace=True)
            combined_df.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, index=False)

        logging.info("Scraping successful. Data saved to scraped_data.csv")

    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

# Scheduler to run every 30 seconds
if __name__ == "__main__":
    schedule.every(30).seconds.do(scrape_jobs)
    print("Scraper is running every 30 seconds... Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
