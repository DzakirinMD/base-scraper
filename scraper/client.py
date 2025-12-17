import requests
import json
import os

class WebClient:
    def __init__(self, baseUrl, email, password, token=None):
        self.base_url = baseUrl
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token = token
        os.makedirs('data', exist_ok=True)

        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def login(self):
        login_url = f"{self.base_url}/login"
        payload = {"email": self.email, "password": self.password, "error": ""}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            print("Attempting fresh login...")
            response = self.session.post(login_url, json=payload, headers=headers)
            data = response.json()
            if data.get("success"):
                self.token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                with open("data/token.txt", "w") as f: f.write(self.token)
                print(f"✓ New login successful.")
                return True
            return False
        except Exception as e:
            print(f"✗ Login Error: {e}")
            return False

    def search_facilities(self, category, location_id, search_date):
        url = f"{self.base_url}/location/facility"
        params = {"sub_category": category, "location_id": location_id, "search_date": search_date}
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 401: return {"success": False, "error": "unauthorized"}
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ API Error for Location {location_id}: {e}")
            return None

    def save_to_json(self, data, filename):
        filepath = os.path.join('data', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
