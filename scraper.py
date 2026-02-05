from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

coords = "18.613597081270246,73.8165830558739"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

#Open maps with coordinates
driver.get(f"https://www.google.com/maps/search/{coords}")

#Click Nearby
nearby_btn = wait.until(
    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Nearby"]'))
)
nearby_btn.click()

#Wait (cursor auto-focus)
time.sleep(2)

#Type hospitals
driver.switch_to.active_element.send_keys("hospitals")
driver.switch_to.active_element.send_keys(Keys.ENTER)

#Wait for results to load
time.sleep(7)

#Get all result cards
cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")

print("\nHospitals Found:\n")

for card in cards:
    try:
        # Hospital name
        name = card.find_element(By.CLASS_NAME, "qBF1Pd").text
        
        # Place link
        place_link = card.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
        
        # Directions link
        directions_link = place_link.replace("/place/", "/dir/?api=1&destination=")

        print("Name:", name)
        print("Directions:", directions_link)
        print("-" * 50)

    except:
        pass

driver.quit()
