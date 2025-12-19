import os
import shutil
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from scraper.client import WebClient

load_dotenv()

def clear_data_folder():
    """Clears the /data folder except for token.txt"""
    folder = 'data'
    if not os.path.exists(folder):
        os.makedirs(folder)
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                # Don't delete the auth token to save time on re-login
                if "token" not in filename: 
                    os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def get_dates_based_on_mode(mode: str, specific_date: str = None):
    """Generates the list of dates based on the requested mode."""
    today = datetime.now()
    dates = []
    
    # Mode 1: Weekends only (Fri, Sat, Sun) for next 21 days
    if mode == "weekend":
        dates = [
            (today + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(1, 22) 
            if (today + timedelta(days=i)).weekday() in [4, 5, 6]
        ]
    
    # Mode 2: All days for next 21 days
    elif mode == "all":
        dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 22)]
    
    # Mode 3: Specific single date
    elif mode == "single":
        if not specific_date:
            raise ValueError("Date must be provided for 'single' mode")
        
        target = datetime.strptime(specific_date, "%Y-%m-%d")
        max_date = today + timedelta(days=21)
        
        # Validation: Must be within next 21 days
        if target.date() < today.date() or target.date() > max_date.date():
            raise ValueError(f"Date {specific_date} is out of range (Must be within next 21 days)")
            
        dates = [specific_date]
        
    return dates

def run_scraper_process(mode: str, specific_date: str = None):
    """The main scraping worker function."""
    
    # 1. Clean Data Folder
    print("🧹 Cleaning data folder...")
    clear_data_folder()

    # 2. Setup Client
    baseUrl = os.getenv("WEB_BASE_URL")
    email = os.getenv("WEB_EMAIL")
    password = os.getenv("WEB_PASSWORD")
    token = os.getenv("WEB_TOKEN")

    client = WebClient(baseUrl, email, password, token=token)

    # 3. Authenticate
    is_authenticated = False
    if token:
        test_search = client.search_facilities("TENIS", 9, datetime.now().strftime('%Y-%m-%d'))
        if test_search and test_search.get("success"):
            is_authenticated = True
    
    if not is_authenticated:
        if client.login():
            set_key(".env", "WEB_TOKEN", client.token)
        else:
            print("Auth failed. Aborting.")
            return {"status": "failed", "reason": "Authentication failed"}

    # 4. Get Dates
    try:
        target_dates = get_dates_based_on_mode(mode, specific_date)
    except ValueError as e:
        return {"status": "failed", "reason": str(e)}

    # 5. Scrape
    LOCATION_IDS = [9, 10, 15] 
    CATEGORY = "TENIS"
    target_names = [f"COURT {i}" for i in range(1, 11)] + [f"GELANGGANG {i}" for i in range(1, 11)]

    print(f"🚀 Starting scrape for {len(target_dates)} dates...")
    
    for loc_id in LOCATION_IDS:
        for date_str in target_dates:
            print(f"Processing {date_str} @ Loc {loc_id}")
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
            time.sleep(1) # Rate limit protection

    print("✅ Scraping complete.")
    return {"status": "success", "dates_processed": len(target_dates)}