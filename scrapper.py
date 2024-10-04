import csv
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_interpol_red_notices():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    options.add_argument('--headless')  
    options.add_argument("--disable-software-rasterizer")
    options.page_load_strategy = 'normal'  
    options.add_argument('--start-maximized')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get('https://www.interpol.int/en/How-we-work/Notices/Red-Notices/View-Red-Notices')

    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.redNoticeItem__labelLink')))

    red_notices = []
    current_page = 1

    try:
        while True:

            notices = driver.find_elements(By.CSS_SELECTOR, '.redNoticeItem__labelLink')

            for notice in notices:
                name = notice.text.strip()  # Get the name text
                red_notices.append({'name': name})  # Store only the name

            # Check for pagination links
            try:
        
                page_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="page="]')

                next_page_link = None
                for link in page_links:
                    page_number = link.text.strip()
                    if page_number.isdigit() and int(page_number) > current_page:
                        next_page_link = link
                        break

                if next_page_link:
                    next_page_link.click()

                    WebDriverWait(driver, 10).until(EC.staleness_of(notices[0]))  # Wait until the old notices are stale
                    time.sleep(2)  

        
                    current_page += 1
                else:
                    print("No more pages to scrape.")
                    break

            except Exception as e:
                print("Error occurred while navigating pages:", e)
                break

    finally:
        driver.quit()  
    
    save_red_notices_to_csv(red_notices)

def save_red_notices_to_csv(red_notices):

    os.makedirs('output', exist_ok=True)

    with open('output/red_notices.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name'])
        writer.writeheader()
        for notice in red_notices:
            writer.writerow(notice)
            logging.info(f'Written to CSV: {notice}')  # Log each written notice

