import json
import os
from datetime import datetime

def generate_html():
    data_dir = 'data'
    # Get all JSON files excluding token
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and not f.startswith('token')]
    
    # --- Step 1: Grouping Logic (Date -> Location -> Court) ---
    hierarchy = {}

    for file_name in json_files:
        try:
            with open(os.path.join(data_dir, file_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                date = data.get("search_date")
                loc = data.get("location_name")
                
                if date not in hierarchy: hierarchy[date] = {}
                if loc not in hierarchy[date]: hierarchy[date][loc] = []
                
                hierarchy[date][loc].append(data)
        except Exception as e:
            print(f"Skipping {file_name} due to error: {e}")

    # --- Step 2: Build HTML & Modern CSS ---
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sport Booking Dashboard</title>
        <style>
            :root { --primary: #2563eb; --success: #22c55e; --danger: #ef4444; --bg: #f8fafc; }
            body { font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: #1e293b; margin: 0; padding: 2rem; }
            .container { max-width: 1100px; margin: 0 auto; }
            
            /* Date Header */
            .date-block { background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 2.5rem; overflow: hidden; border: 1px solid #e2e8f0; }
            .date-header { background: var(--primary); color: white; padding: 1rem 1.5rem; font-size: 1.5rem; font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
            
            /* Location & Court Layout */
            .location-container { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; }
            .location-name { font-size: 1.1rem; font-weight: 600; color: var(--primary); margin-bottom: 1rem; display: flex; align-items: center; }
            .location-name::before { content: '📍'; margin-right: 8px; }
            
            .court-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
            .court-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; background: #fff; }
            .court-title { font-weight: 700; margin-bottom: 0.5rem; border-bottom: 1px solid #eee; padding-bottom: 4px; }
            
            /* Slot Table */
            table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
            th { text-align: left; color: #64748b; font-weight: 600; padding: 4px; }
            td { padding: 6px 4px; border-bottom: 1px solid #f8fafc; }
            
            .available { color: var(--success); font-weight: 600; }
            .booked { color: #cbd5e1; text-decoration: line-through; }
            .price-tag { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600; }

            .filter-btn { background: white; color: var(--primary); border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; }
        </style>
        <script>
            function toggleBooked() {
                const bookedRows = document.querySelectorAll('.booked-row');
                bookedRows.forEach(row => row.style.display = row.style.display === 'none' ? 'table-row' : 'none');
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h1>📅 Booking Explorer</h1>
                <button class="filter-btn" onclick="toggleBooked()">Toggle Booked Slots</button>
            </div>
    """

    # --- Step 3: Iterate through hierarchy (Sorted by Date) ---
    for date in sorted(hierarchy.keys()):
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %d %b %Y')
        html_template += f"""
        <div class="date-block">
            <div class="date-header">
                <span>{formatted_date}</span>
            </div>
        """
        
        # Sort locations by name
        for loc in sorted(hierarchy[date].keys()):
            html_template += f"""
            <div class="location-container">
                <div class="location-name">{loc}</div>
                <div class="court-grid">
            """
            
            # Sort courts by name
            courts = sorted(hierarchy[date][loc], key=lambda x: x['venue_name'])
            for court in courts:
                html_template += f"""
                    <div class="court-card">
                        <div class="court-title">{court['venue_name']}</div>
                        <table>
                            <thead>
                                <tr><th>Time</th><th>Price</th><th>Status</th></tr>
                            </thead>
                            <tbody>
                """
                
                for s in court['location_facility_times']:
                    is_available = s['slot_available']
                    row_class = "" if is_available else "booked-row"
                    status_class = "available" if is_available else "booked"
                    status_text = "FREE" if is_available else "Booked"
                    
                    html_template += f"""
                                <tr class="{row_class}">
                                    <td>{s['start_time_value']} - {s['end_time_value']}</td>
                                    <td><span class="price-tag">RM{float(s['price']):.0f}</span></td>
                                    <td class="{status_class}">{status_text}</td>
                                </tr>
                    """
                html_template += "</tbody></table></div>"
            html_template += "</div></div>"
        html_template += "</div>"

    html_template += "</div></body></html>"

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"✓ Reorganized dashboard generated: {os.path.abspath('dashboard.html')}")

if __name__ == "__main__":
    generate_html()