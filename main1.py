from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import socket

app = FastAPI()

def get_local_ip():
    """Helper to find the local network IP of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_common_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false") # Don't load images (much faster)
    chrome_options.add_argument("--window-size=1920,1080")
    return chrome_options

def scrape_hospitals(disease: str, lat: float, lon: float):
    coords = f"{lat},{lon}"
    chrome_options = get_common_chrome_options()
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15) 
    hospitals = []

    try:
        driver.get(f"https://www.google.com/maps/search/{coords}")

        nearby_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label,"Nearby")]'))
        )
        nearby_btn.click()

        time.sleep(1)

        search_query = f"{disease} hospitals clinics"
        active_element = driver.switch_to.active_element
        active_element.send_keys(search_query)
        active_element.send_keys("\n")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        time.sleep(2)

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

                link = card.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")

                hospitals.append({
                    "name": name,
                    "rating": rating_float,
                    "phone": phone,
                    "link": link
                })
            except:
                continue

        return sorted(hospitals, key=lambda x: x["rating"], reverse=True)[:5]

    finally:
        driver.quit()

def scrape_nearby_ambulance(lat: float, lon: float):
    coords = f"{lat},{lon}"
    chrome_options = get_common_chrome_options()

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    ambulances = []

    try:
        driver.get(f"https://www.google.com/maps/search/{coords}")

        nearby_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label,"Nearby")]'))
        )
        nearby_btn.click()

        time.sleep(1)

        active_element = driver.switch_to.active_element
        active_element.send_keys("ambulance service")
        active_element.send_keys("\n")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        time.sleep(2)

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

                link = card.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")

                ambulances.append({
                    "name": name,
                    "rating": rating_float,
                    "phone": phone,
                    "link": link
                })
            except:
                continue

        return sorted(ambulances, key=lambda x: x["rating"], reverse=True)[:5]

    finally:
        driver.quit()

@app.get("/")
def home():
    local_ip = get_local_ip()
    # Using port 5000 as requested for ngrok
    return {
        "status": "API Running Locally",
        "endpoints": {
            "hospitals": f"http://{local_ip}:5000/hospitals?disease=heart&lat=18.6135&lon=73.8165",
            "ambulance": f"http://{local_ip}:5000/ambulance?lat=18.6135&lon=73.8165"
        },
        "instruction": "Send requests to these URLs from any device on your Wi-Fi."
    }

@app.get("/hospitals")
def get_hospitals(disease: str, lat: float, lon: float):
    try:
        results = scrape_hospitals(disease, lat, lon)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

@app.get("/ambulance")
def get_ambulance(lat: float, lon: float):
    try:
        results = scrape_nearby_ambulance(lat, lon)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    print(f"\n--- SERVER STARTING ---")
    print(f"Local Access: http://127.0.0.1:5000")
    print(f"Network Access: http://{local_ip}:5000")
    print(f"-----------------------\n")
    uvicorn.run(app, host="0.0.0.0", port=5000)


 