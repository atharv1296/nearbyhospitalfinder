from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API Running"}

@app.get("/hospitals")
def get_hospitals(coords: str = Query(...)):
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # Open maps with coordinates
        driver.get(f"https://www.google.com/maps/search/{coords}")

        # Click Nearby
        nearby_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Nearby"]'))
        )
        nearby_btn.click()

        time.sleep(2)

        # Type hospitals
        driver.switch_to.active_element.send_keys("hospitals")
        driver.switch_to.active_element.send_keys(Keys.ENTER)

        time.sleep(7)

        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        results = []

        for card in cards:
            try:
                name = card.find_element(By.CLASS_NAME, "qBF1Pd").text
                place_link = card.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
                directions_link = place_link.replace("/place/", "/dir/?api=1&destination=")

                results.append({
                    "name": name,
                    "directions": directions_link
                })
            except:
                pass

        return results

    finally:
        driver.quit()
