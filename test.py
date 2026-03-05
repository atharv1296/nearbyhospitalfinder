import requests
import time

# Your Render API URL
BASE_URL = "https://nearbyhospitalfinder-1.onrender.com"

# Endpoint
endpoint = "/hospitals"

# Parameters
params = {
    "disease": "cancer",
    "lat": 18.5587,
    "lon": 19.2458
}

try:
    print("Sending request to API...")
    
    start_time = time.time()
    
    response = requests.get(BASE_URL + endpoint, params=params)
    
    end_time = time.time()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Time: {end_time - start_time:.2f} seconds")
    
    data = response.json()
    
    print("\nHospitals found:\n")
    
    if "results" in data:
        for i, hospital in enumerate(data["results"], 1):
            print(f"{i}. Name: {hospital['name']}")
            print(f"   Rating: {hospital['rating']}")
            print(f"   Phone: {hospital['phone']}")
            print(f"   Link: {hospital['link']}")
            print()
    else:
        print(data)

except Exception as e:
    print("Error:", str(e))