from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validator
from typing import Optional
import re

# Import logic from other files
from scraper.service import run_scraper_process
from templates.visualize import generate_dashboard_html

app = FastAPI(title="Sport Booking Scraper Microservice")

# --- Input Models ---
class ScrapeRequest(BaseModel):
    mode: str  # Options: 'weekend', 'all', 'single'
    date: Optional[str] = None # Format: YYYY-MM-DD (Only for 'single' mode)

    @validator('mode')
    def validate_mode(cls, v):
        allowed = ['weekend', 'all', 'single']
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v

    @validator('date')
    def validate_date_format(cls, v):
        if v and not re.match(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

# --- API Endpoints ---

@app.post("/scrape")
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    API 1: Trigger the scraping process.
    - mode='weekend': Next 21 days (Fri, Sat, Sun)
    - mode='all': Next 21 days (All)
    - mode='single': Specific date (must provide 'date' field)
    """
    
    # Quick Validation for Single Mode
    if request.mode == 'single' and not request.date:
        raise HTTPException(status_code=400, detail="Date is required for 'single' mode")

    # Run scraper in background so API returns immediately
    background_tasks.add_task(run_scraper_process, request.mode, request.date)
    
    return {
        "message": "Scraping started in background", 
        "config": {
            "mode": request.mode, 
            "target_date": request.date if request.mode == 'single' else "Range"
        }
    }

@app.get("/visualize", response_class=HTMLResponse)
async def get_dashboard():
    """
    API 2: Generate and serve the dashboard HTML.
    """
    html_content = generate_dashboard_html()
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)