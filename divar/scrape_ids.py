import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Base URL
MAIN_PAGE_URL = "https://divar.ir/s/tehran/rent-residential"
SAVE_FILE = "divar_tehran_post_ids.csv"  # File to save post IDs

chrome_path = "/home/mohammad/chrome-linux64/chrome"  # Adjust path if needed

options = Options()
options.binary_location = chrome_path
#options.add_argument("--headless")  # REMOVE HEADLESS MODE to allow user confirmation
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

service = ChromeService(executable_path="/home/mohammad/chromedriver-linux64/chromedriver")  # Adjust path
driver = webdriver.Chrome(service=service, options=options)

def load_existing_ids():
    """Load existing post IDs from the CSV file to avoid duplicates."""
    if os.path.exists(SAVE_FILE):
        df = pd.read_csv(SAVE_FILE)
        return set(df["post_id"])
    return set()

def save_post_ids(post_ids):
    """Save new post IDs to the CSV file."""
    df = pd.DataFrame({"post_id": list(post_ids)})
    df.to_csv(SAVE_FILE, index=False)
    print(f"✅ Saved {len(post_ids)} post IDs to {SAVE_FILE}")

def confirm_continue():
    """Ask user for confirmation to continue scrolling."""
    print("\n🚀 **PAUSED: Check the browser!**")
    print("If more listings exist, press [Enter] to continue scrolling.")
    print("If at the end, type 'end' and press [Enter] to stop.")
    user_input = input("➡️ Continue or End? ").strip().lower()
    return user_input != "end"

def click_retry_button():
    """Click the 'تلاش دوباره' (Retry) button if it appears."""
    try:
        retry_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "error-message__button-c35bb"))
        )
        retry_button.click()
        print("🔄 Clicked 'تلاش دوباره' (Retry) button.")
        time.sleep(3)  # Wait for new listings to load
        return True
    except:
        return False  # No button found

def get_all_post_ids():
    """Scrape all post IDs by scrolling and clicking buttons when needed."""
    driver.get(MAIN_PAGE_URL)
    existing_ids = load_existing_ids()
    all_post_ids = existing_ids.copy()  # Keep old post IDs
    last_height = driver.execute_script("return document.body.scrollHeight")  # Initial page height
    scroll_attempts = 0

    while True:
        try:
            # Extract post IDs
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            links = soup.find_all("a", class_="kt-post-card__action")
            post_ids = {link["href"].split("/")[-1] for link in links if "/v/" in link["href"]}

            new_ids = post_ids - all_post_ids  # Only keep new ones
            print(f"🔍 New listings found: {len(new_ids)}")
            all_post_ids.update(new_ids)  # Add new IDs to the set

            # Click "آگهی‌های بیشتر" button if present
            try:
                load_more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "post-list__load-more-btn-be092"))
                )
                load_more_button.click()
                print("📌 Clicked 'آگهی‌های بیشتر' (Load More Ads) button.")
                time.sleep(3)  # Wait for new listings to load
            except:
                pass  # No button found, continue scrolling

            # Check and click "تلاش دوباره" (Retry) button if it appears
            if click_retry_button():
                continue  # Restart loop after clicking retry button

            # Scroll down to load more listings
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load

            # Check if the page height changes (if no change, stop scrolling)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 5:  
                    if confirm_continue():
                        scroll_attempts = 0  # Reset attempts if user wants to continue
                    else:
                        break  # Stop scraping
            else:
                scroll_attempts = 0  # Reset attempts if new content loads
            last_height = new_height

        except Exception as e:
            print(f"❌ Error: {e}")
            break

    driver.quit()
    save_post_ids(all_post_ids)
    return list(all_post_ids)

# Run the scraper
post_ids = get_all_post_ids()
print(f"✅ Total listings scraped: {len(post_ids)}")
