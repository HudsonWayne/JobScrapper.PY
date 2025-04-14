h# web_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Target URL
URL = "https://vacancymail.co.zw/jobs/"

# Scraping function
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

            # Get job description from the job page
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

        # Save as CSV
        df.to_csv("scraped_data.csv", index=False)
        logging.info("Scraping successful. Data saved to scraped_data.csv")

    except Exception as e:
        logging.error(f"Scraping failed: {e}")

# Schedule the job
def schedule_scraping():
    schedule.every().day.at("10:00").do(scrape_jobs)  # adjust time as needed

    print("Scheduled scraping every day at 10:00AM. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    scrape_jobs()  
   
