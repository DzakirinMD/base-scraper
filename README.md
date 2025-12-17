# Web Scraper & Visualizer

A Python-based tool to authenticate with the web portal, scrape court availability across multiple locations, and visualize the data in an easy-to-read format.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Environment Setup
Create a `.env` file in the root directory and add your credentials:
- WEB_BASE_URL = https://something.website 
- WEB_EMAIL = your_email@example.com
- WEB_PASSWORD = your_secure_password
- WEB_TOKEN = YOUR_TOKEN

### 3. Install Dependencies
Open your terminal in the project folder and run:

```
# Create python virtual environment
python -m venv .venv

# Activate python virtual environment
.\.venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt
```

### 4. Running the Scraper
To execute the scraping and parsing logic:
`
python main.py
`

### 5. Visualize the Data
Run the visualizer to generate an HTML dashboard:
`
python visualize.py
` 

Then, open `data/dashboard.html` in your browser.

### 6. Output
The results of the scrape will be saved in the `/data` folder. 

### 6. Folder Structure
```
base_scraper/
│
├── main.py                # Entry point (executes login & scraping)
├── visualize.py           # Dashboard generator
├── scraper/
│   ├── __init__.py
│   ├── client.py          # API interaction and CSV parsing logic
├── data/                  # Directory where CSV files will be saved
├── .env                   # Environment variables (Credentials)
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```
