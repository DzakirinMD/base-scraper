import json
import os
from datetime import datetime

def generate_dashboard_html():
    data_dir = 'data'
    template_path = os.path.join('templates', 'dashboard.html')
    
    # 1. Read the Template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
    except FileNotFoundError:
        return "<h1>Error: Template file not found in /templates/dashboard.html</h1>"

    if not os.path.exists(data_dir):
        return html_template.replace("{{content}}", "<div class='no-data'><h2>No Data Folder Found</h2></div>")

    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and not f.startswith('token')]
    
    if not json_files:
        return html_template.replace("{{content}}", "<div class='no-data'><h2>No Data Available</h2><p>Run the scraper first.</p></div>")

    # 2. Process Data
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
            print(f"Skipping {file_name}: {e}")

    # 3. Build HTML Fragments
    generated_html = ""
    
    for date in sorted(hierarchy.keys()):
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %d %b %Y')
        
        generated_html += f"""
        <div class="date-block" data-date="{date}">
            <div class="date-header">{formatted_date}</div>
        """
        
        for loc in sorted(hierarchy[date].keys()):
            generated_html += f"""
            <div class="location-container">
                <div class="location-name">{loc}</div>
                <div class="court-grid">
            """
            
            courts = sorted(hierarchy[date][loc], key=lambda x: x['venue_name'])
            for court in courts:
                generated_html += f"""
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
                    price = float(s['price']) if s['price'] else 0
                    
                    generated_html += f"""
                            <tr class="{row_class}">
                                <td>{s['start_time_value']} - {s['end_time_value']}</td>
                                <td><span class="price-tag">RM{price:.0f}</span></td>
                                <td class="{status_class}">{status_text}</td>
                            </tr>
                    """
                generated_html += "</tbody></table></div>" # End Court Card
            
            generated_html += "</div></div>" # End Location Container
        
        generated_html += "</div>" # End Date Block

    # 4. Inject into Template
    final_html = html_template.replace("{{content}}", generated_html)
    
    return final_html