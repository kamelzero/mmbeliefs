import time
import json
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup
import tqdm
import os
import requests

driver_path = "/snap/bin/geckodriver"
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(service=Service(executable_path=driver_path), options=options)

def save_results(results, fn='results.json'):
    with open(fn, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {fn}")

def get_content(url, headless=False, fn='results.json'):
    print(f"Getting content from {url}")

    # options = Options()
    # if headless:
    #     options.add_argument("--headless")
    # options.add_argument("--no-sandbox")

    driver.get(url)

    # Wait for initial page load
    wait = WebDriverWait(driver, 10)
    
    results = []
    previous_length = 0
    i = 0
    while True:
        print(f"Step = {i}")
        try:
            # First scroll down aggressively to make sure we can see the button
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll up a bit to trigger any lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)
            
            # Check if "See More" button exists
            buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "See More")]')
            if not buttons:
                print("No more 'See More' buttons found. Finished loading all content.")
                break

            # Wait for button to be present and clickable
            button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "See More")]')))
            
            # Get button location and scroll to it with offset
            location = button.location
            driver.execute_script(f"window.scrollTo(0, {location['y'] - 300});")
            time.sleep(1)
            
            # Try to click using JavaScript if regular click fails
            try:
                button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", button)
            
            # Wait for new content to load
            time.sleep(3)
            
            # Get current content
            html = driver.page_source
            results = get_card_info(html)
            save_results(results, fn=fn)
            
            # Check if we got any new items
            if len(results) <= previous_length: # and len(current_results) > 1000:
                print("No new items loaded. Stopping.")
                break
                
            previous_length = len(results)
            print(f"Found {len(results)} items so far...")

            i += 1
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            time.sleep(2)
            continue
        
    driver.quit()
    return results

def get_card_info(html):
    results = []

    soup = BeautifulSoup(html, 'html.parser')
    muiboxes = soup.select('div.list-item-wrapper.MuiBox-root.css-1ycirx')
    for muibox in muiboxes:
        res = {}
        res['title'] = muibox.find('h2').text.strip()
        for detail in muibox.select('div.label-wrapper'):
            if len(detail.select('div.MuiChip-root')) > 0:
                name = detail.find('p').text.strip()
                values = []
                for chip in detail.select('div.MuiChip-root'):
                    values.append(chip.text.strip())
                res[name] = values
            elif len(detail.select('div.sw-width-s')) > 0:
                name = detail.find('p').text.strip() # description
                value = detail.find('div').text.strip()
                res[name] = value
        results.append(res)
        static_images = muibox.find_all('div', class_='static-image')
        res_image_urls = []
        for image in static_images:
            style = image['style']
            res_image_urls.append(style.split('url(')[1].split(')')[0].strip('"'))
        res['images'] = res_image_urls
    return results

def scrape_gpahe_symbols(fn='results.json'):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print("Opening GPAHE...")
        gpahe_db_url = "https://globalextremism.org/global-extremist-symbols-database/"
        page.goto(gpahe_db_url)

        print("Waiting for initial JS to load")
        time.sleep(5)  # Let initial JS load

        # Scroll in steps until bottom of page reached
        previous_height = 0
        scroll_pause_time = 2

        # Scroll down until no more content to scroll
        print("Scrolling down...")
        while True:
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(scroll_pause_time * 1000)
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                print("✅ No more content to scroll.")
                break
            previous_height = current_height

        print("📦 Page has", len(page.frames), "frames")
        if len(page.frames) >= 2 and page.frames[0].url == gpahe_db_url:
            content_page_url = page.frames[1].url
        else:
            print("❌ Unexpected page structure.")
            return

        print("Getting content...")
        results = get_content(content_page_url, headless=True, fn=fn)
        browser.close()
    return results

def download_images(results, images_dir='images', output_fn='results_with_images.json'):
    os.makedirs(images_dir, exist_ok=True)

    for index, result in tqdm.tqdm(enumerate(results)):
        images = result['images']
        for img_index, image in enumerate(images):
            try:
                response = requests.get(image)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # Try to get content type from headers, default to 'png' if not found
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'
                elif 'svg' in content_type:
                    ext = 'svg'
                else:
                    ext = 'png'  # Default to PNG if content-type is unknown                    
                filename = f"{images_dir}/{index}_{img_index}.{ext}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Error downloading {image}: {e}")
            results[index]['images'][img_index] = filename

    with open(output_fn, 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    results = scrape_gpahe_symbols(fn='results.json')
    download_images(results, images_dir='images', output_fn='results_with_images.json')
