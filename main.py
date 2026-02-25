from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

app = FastAPI()

def scrape_hospitals(disease: str, lat: float, lon: float):
    coords = f"{lat},{lon}"
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    hospitals = []

    try:
        driver.get(f"https://www.google.com/maps/search/{coords}")

        # Click "Nearby" button
        nearby_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Nearby"]'))
        )
        nearby_btn.click()

        time.sleep(2)

        # Search for specific disease clinics
        search_query = f"{disease} hospitals/clinics near me"
        active_element = driver.switch_to.active_element
        active_element.send_keys(search_query)
        active_element.send_keys("\n")

        # Wait for results to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        time.sleep(3)

        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        for card in cards:
            try:
                name = card.find_element(By.CLASS_NAME, "qBF1Pd").text

                try:
                    rating = card.find_element(By.CLASS_NAME, "MW4etd").text
                    rating_float = float(rating)
                except:
                    rating_float = 0.0

                try:
                    phone = card.find_element(By.CLASS_NAME, "UsdlK").text
                except:
                    phone = "N/A"

                place_link = card.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")

                hospitals.append({
                    "name": name,
                    "rating": rating_float,
                    "phone": phone,
                    "link": place_link
                })

            except:
                continue

        # Sort by rating (highest first) and take Top 5
        hospitals_sorted = sorted(hospitals, key=lambda x: x["rating"], reverse=True)
        return hospitals_sorted[:5]

    finally:
        driver.quit()

@app.get("/")
def home():
    return {"status": "Nearby Hospital API is Running", "instruction": "Use /hospitals?disease=...&lat=...&lon=..."}

@app.get("/hospitals")
def get_hospitals(
    disease: str = Query(..., description="The type of disease or specialist to search for"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        results = scrape_hospitals(disease, lat, lon)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
