# Web Scraper & Visualizer Microservice

A Python-based tool powered by **FastAPI** to authenticate with the web portal, scrape court availability, and serve a visualized HTML dashboard via a RESTful API.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Environment Setup
Create a `.env` file in the root directory and add your credentials:
- `WEB_BASE_URL` = https://something.website 
- `WEB_EMAIL` = your_email@example.com
- `WEB_PASSWORD` = your_secure_password
- `WEB_TOKEN` = YOUR_TOKEN (Optional, will be generated automatically if missing)

### 3. Install Dependencies
Open your terminal in the project folder and run:

```bash
# Create python virtual environment
python -m venv .venv

# Activate python virtual environment
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 4. Running the Application
Start the FastAPI server. This will serve both the scraping endpoints and the dashboard.

```bash
python main.py
# OR if you have uvicorn installed directly
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`



### 5. API Endpoints
1. Scrape Weekends
Triggers a background task to scrape data for Fridays, Saturdays, and Sundays for the next 21 days.

- URL: `POST /scrape`
- Body:
```json

{
    "mode": "weekend"
}
```

2. Scrape All Days
Triggers a background task to scrape every day for the next 21 days.

- URL: `POST /scrape`

- Body:
```json
{
    "mode": "all"
}
```

3. Scrape Single Date
Triggers a background task to scrape a specific date.

- URL: `POST /scrape`

- Note: The date must be within the next 21 days.

- Body:
```json
{
    "mode": "single",
    "date": "2025-12-25"
}
```

4. View Dashboard
Renders the HTML visualization of the scraped data.

- URL: `GET /visualize`

- Usage: Open `http://127.0.0.1:8000/visualize` in your web browser.

### 5. Folder Structure
```
base_scraper/
│
├── main.py                # FastAPI Application entry point
├── templates/
│   ├── dashboard.html     # HTML Template for the visualization
|   └── visualize.py       # Dashboard generation logic
├── scraper/
│   ├── client.py          # HTTP Client (Login & API calls)
|   └── service.py         # Business logic (Scraping worker & File cleanup)
├── data/                  # Directory where JSON data is stored
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```
