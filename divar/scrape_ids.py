import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Base URLs
MAIN_PAGE_URL = "https://divar.ir/s/tehran/rent-residential"
API_URL = "https://api.divar.ir/v8/posts-v2/web/{}"

chrome_path = "/home/mohammad/chrome-linux64/chrome"  # Adjust if needed

options = Options()
options.binary_location = chrome_path

# Headers (we might not need headers with Selenium, but it's good practice to include)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def get_post_ids_with_selenium():
    """Scrapes post IDs using Selenium to handle JavaScript rendering."""
    service = ChromeService(executable_path='/home/mohammad/chromedriver-linux64/chromedriver') # <-- Replace with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=options) # Or use other browser drivers like Firefox, Edge
    driver.get(MAIN_PAGE_URL)

    try:
        # Wait for listings to load (adjust timeout as needed, e.g., 10 seconds)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kt-post-card__action"))
        )

        # Get the rendered HTML source
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")

        links = soup.find_all("a", class_="kt-post-card__action")
        print(f"Links found by Selenium: {len(links)}") # Check if Selenium finds links

        post_ids = [link["href"].split("/")[-1] for link in links if "/v/" in link["href"]]
        return post_ids[:10] # Get first 10 listings

    except Exception as e:
        print(f"Error during Selenium scraping: {e}")
        return []
    finally:
        driver.quit() # Close the browser window

# Get post IDs using Selenium
post_ids = get_post_ids_with_selenium()
print(post_ids)