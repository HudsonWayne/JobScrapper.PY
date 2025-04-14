import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import datetime
import logging
import schedule
import time


logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

URL = "https://vacancymail.co.zw/jobs/"
CSV_FILE = "scraped_data.csv"

def scrape_jobs():
    try:
        logging.info("Started scraping...")
        response = requests.get(URL)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        
        with open("page_source.html", "w", encoding='utf-8') as f:
            f.write(soup.prettify())

        job_cards = soup.find_all('a', class_='job-listing')

        if not job_cards:
            logging.error("No job cards found.")
            return

        jobs = []
        for card in job_cards:
            title_tag = card.find('h3', class_='job-listing-title')
            title = title_tag.text.strip() if title_tag else "N/A"

            company_tag = card.find('h4', class_='job-listing-company')
            company = company_tag.text.strip() if company_tag else "N/A"

            desc_tag = card.find('p', class_='job-listing-text')
            description = desc_tag.text.strip() if desc_tag else "N/A"

            footer = card.find('div', class_='job-listing-footer')
            location = "N/A"
            expiry = "N/A"
            job_type = "N/A"
            salary = "N/A"
            posted = "N/A"

            if footer:
                lis = footer.find_all('li')
                if len(lis) >= 5:
                    location = lis[0].text.strip()
                    expiry = lis[1].text.strip()
                    job_type = lis[2].text.strip()
                    salary = lis[3].text.strip()
                    posted = lis[4].text.strip()

            jobs.append({
                "Title": title,
                "Company": company,
                "Description": description,
                "Location": location,
                "Expiry": expiry,
                "Job Type": job_type,
                "Salary": salary,
                "Posted": posted,
                "Scraped Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        df = pd.DataFrame(jobs)

        
        if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
            df.to_csv(CSV_FILE, index=False)
            logging.info("New file created and data saved.")
        else:
            df.to_csv(CSV_FILE, mode='a', header=False, index=False)
            logging.info("Data appended to existing file.")

    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        print(e)

def schedule_scraping():
    schedule.every(30).seconds.do(scrape_jobs)
    print("Scraper is running every 30 seconds... Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    scrape_jobs()  
    schedule_scraping()
