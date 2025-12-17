import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from scraper.client import WebClient

load_dotenv()

def main():
    baseUrl = os.getenv("WEB_BASE_URL")
    email = os.getenv("WEB_EMAIL")
    password = os.getenv("WEB_PASSWORD")
    token = os.getenv("WEB_TOKEN")

    client = WebClient(baseUrl, email, password, token=token)
    
    # --- Authentication Block ---
    is_authenticated = False
    if token:
        print("Checking existing token...")
        test_search = client.search_facilities("TENIS", 9, datetime.now().strftime('%Y-%m-%d'))
        if test_search and test_search.get("success"):
            print("✓ Token valid.")
            is_authenticated = True
        else:
            print("! Token invalid/expired.")

    if not is_authenticated:
        if client.login():
            set_key(".env", "WEB_TOKEN", client.token)
            is_authenticated = True
        else:
            print("✗ Auth Failed."); return

    # --- Configuration ---
    LOCATION_IDS = [9, 10, 15] 
    CATEGORY = "TENIS"
    # Generate dates for the next 21 days, filtering only for Fri, Sat, and Sun
    dates = [
        (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') 
        for i in range(1, 22) 
        if (datetime.now() + timedelta(days=i)).weekday() in [4, 5, 6]
    ]
    # Generate dates for the next 21 days, uncomment below to scrape all days
    # dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 22)]
    # Uncomment below code if want to scrape single date
    # dates = ["2026-01-09"]

    target_names = [f"COURT {i}" for i in range(1, 11)] + [f"GELANGGANG {i}" for i in range(1, 11)]
    
    for loc_id in LOCATION_IDS:
        print(f"\n--- Scraping Location ID: {loc_id} ---")
        for date_str in dates:
            print(f"  Fetching Date: {date_str}...")
            result = client.search_facilities(CATEGORY, loc_id, date_str)
            
            if result and result.get("success"):
                venues = result.get("data", {}).get("data", [])
                if not venues: continue
                
                loc_slug = venues[0].get("location_name", "Unknown").lower().replace(" ", "_")

                for court_name in target_names:
                    match = next((v for v in venues if v["venue_name"].upper() == court_name), None)
                    if match:
                        fname = f"{loc_slug}_{court_name.lower().replace(' ', '_')}_{date_str}.json"
                        client.save_to_json(match, fname)
            time.sleep(1) # Prevent rate limiting

if __name__ == "__main__":
    main()