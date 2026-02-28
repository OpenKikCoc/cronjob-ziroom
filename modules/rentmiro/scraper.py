import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_api_url():
    """
    Dynamically get the API URL by traversing:
    1. Main page -> iframe src
    2. Iframe content -> window.__APP_CONFIG__ -> sightmaps[0].href
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    try:
        # Step 1: Get main page
        print("Fetching main page...")
        main_url = "https://www.rentmiro.com/floorplans"
        res = requests.get(main_url, headers=headers, timeout=30)
        res.raise_for_status()
        
        # Step 2: Find iframe src
        soup = BeautifulSoup(res.text, 'html.parser')
        iframe = soup.find('iframe', src=re.compile(r'sightmap\.com/embed/'))
        
        if not iframe:
            print("Could not find sightmap iframe on main page")
            # Fallback to known ID if scraping fails
            return "https://sightmap.com/app/api/v1/yjp2k0q9pxl/sightmaps/23140"
            
        iframe_src = iframe['src']
        print(f"Found iframe src: {iframe_src}")
        
        # Step 3: Fetch iframe content
        res_iframe = requests.get(iframe_src, headers=headers, timeout=30)
        res_iframe.raise_for_status()
        
        # Step 4: Extract config
        # Try to match the whole line content for APP_CONFIG
        match = re.search(r'window\.__APP_CONFIG__\s*=\s*({.*})', res_iframe.text)
        if match:
            config_str = match.group(1)
            try:
                config = json.loads(config_str)
                if config.get('sightmaps') and len(config['sightmaps']) > 0:
                    api_url = config['sightmaps'][0]['href']
                    print(f"Found API URL: {api_url}")
                    return api_url
            except json.JSONDecodeError:
                print("Failed to parse JSON config")
                
        print("Could not extract API URL from iframe content")
        return "https://sightmap.com/app/api/v1/yjp2k0q9pxl/sightmaps/23140"
        
    except Exception as e:
        print(f"Error finding API URL: {e}")
        return "https://sightmap.com/app/api/v1/yjp2k0q9pxl/sightmaps/23140"

def scrape_rentmiro_data():
    """Scrape data from RentMiro (via SightMap API)"""
    api_url = get_api_url()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        print(f"Fetching data from API: {api_url}")
        res = requests.get(api_url, headers=headers, timeout=30)
        res.raise_for_status()
        
        data = res.json()
        
        # Process the data
        processed_data = process_api_data(data, api_url)
        return processed_data, 200
        
    except Exception as e:
        return {'error': str(e), 'timestamp': datetime.now().isoformat()}, 500

def process_api_data(api_data, source_url):
    """Process the raw API data into a cleaner format"""
    
    # Create lookup for floor plans
    floor_plans = {}
    if 'data' in api_data and 'floor_plans' in api_data['data']:
        for fp in api_data['data']['floor_plans']:
            floor_plans[fp['id']] = {
                'name': fp.get('name'),
                'beds': fp.get('bedroom_count'),
                'baths': fp.get('bathroom_count'),
                'label': fp.get('filter_label'),
                'image_url': fp.get('image_url')
            }
            
    units = []
    if 'data' in api_data and 'units' in api_data['data']:
        for unit in api_data['data']['units']:
            # Only include available units
            if unit.get('available_on'):
                fp_id = unit.get('floor_plan_id')
                fp_info = floor_plans.get(fp_id, {})
                
                unit_info = {
                    'unit_number': unit.get('unit_number'),
                    'display_unit': unit.get('display_unit_number'),
                    'area': unit.get('area'),
                    'price': unit.get('price'),
                    'display_price': unit.get('display_price'),
                    'available_on': unit.get('available_on'),
                    'floor_plan': fp_info.get('name', 'Unknown'),
                    'beds': fp_info.get('beds'),
                    'baths': fp_info.get('baths'),
                    'floor_plan_image': fp_info.get('image_url'),
                    'floor': unit.get('floor_id'),
                    'price_change': 0  # Default no change
                }
                units.append(unit_info)
    
    # Sort by price (low to high)
    units.sort(key=lambda x: x['price'] if x['price'] else 999999)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'url': source_url,
        'total_units': len(units),
        'units': units
    }
    
    return result

def get_previous_data():
    """Get previous data for comparison"""
    try:
        if os.path.exists('./modules/rentmiro/data.json'):
            with open('./modules/rentmiro/data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

def analyze_changes(current_data, previous_data):
    """Analyze changes between current and previous data"""
    changes = {
        'added': [],
        'removed': [],
        'price_changed': [],
        'date_changed': [],
        'has_changes': False,
        'summary_text': "数据无变化"
    }

    if not previous_data or 'units' not in previous_data:
        changes['summary_text'] = "首次抓取数据，无法比较变化"
        return changes
        
    summary_lines = []
    
    # Create maps for easier comparison
    current_units = {u['unit_number']: u for u in current_data['units']}
    previous_units = {u['unit_number']: u for u in previous_data['units']}
    
    # Check for new units
    for unit_num, unit in current_units.items():
        if unit_num not in previous_units:
            desc = f"{unit['display_unit']} ({unit['floor_plan']}) - {unit['display_price']}"
            changes['added'].append(unit)
            summary_lines.append(f"🏠 新增: {desc}")
            unit['is_new'] = True
        else:
            # Check for price changes
            prev_unit = previous_units[unit_num]
            if unit['price'] != prev_unit['price']:
                diff = unit['price'] - prev_unit['price']
                unit['price_change'] = diff
                symbol = "🔺" if diff > 0 else "🔻"
                desc = f"{unit['display_unit']}: {prev_unit['display_price']} -> {unit['display_price']} ({symbol}{abs(diff)})"
                changes['price_changed'].append({'unit': unit, 'diff': diff, 'desc': desc})
                summary_lines.append(f"💰 调价: {desc}")
            
            # Check for availability date changes
            if unit['available_on'] != prev_unit['available_on']:
                 desc = f"{unit['display_unit']}: {prev_unit['available_on']} -> {unit['available_on']}"
                 changes['date_changed'].append({'unit': unit, 'old_date': prev_unit['available_on'], 'new_date': unit['available_on']})
                 summary_lines.append(f"📅 日期: {desc}")

    # Check for removed units
    for unit_num, unit in previous_units.items():
        if unit_num not in current_units:
            desc = f"{unit['display_unit']} ({unit['floor_plan']})"
            changes['removed'].append(unit)
            summary_lines.append(f"❌ 下架: {desc}")
            
    if summary_lines:
        changes['has_changes'] = True
        changes['summary_text'] = "\n".join(summary_lines)
        
    return changes

def save_data(data, status_code):
    """Save data and generate report"""
    if status_code != 200:
        print(f"❌ 抓取失败: {data.get('error')}")
        return

    print("=== 开始保存数据流程 ===")
    
    # Get previous data
    previous_data = get_previous_data()
    
    # Analyze changes
    changes = analyze_changes(data, previous_data)
    print(f"📈 变化信息:\n{changes['summary_text']}")
    
    # Save current data
    with open('./modules/rentmiro/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # Generate HTML report
    generate_html(data, changes)
    
    print("=== 数据保存流程完成 ===")

def generate_html(data, changes):
    """Generate HTML report"""
    
    # Build changes HTML
    changes_html = ""
    if changes['has_changes']:
        changes_html = '<div class="changes-container">'
        
        if changes['added']:
            changes_html += '<div class="change-section added"><h3>🏠 新增房源</h3><ul>'
            for unit in changes['added']:
                changes_html += f"<li><strong>{unit['display_unit']}</strong> - {unit['floor_plan']} - {unit['display_price']} - {unit['available_on']}</li>"
            changes_html += '</ul></div>'
            
        if changes['removed']:
            changes_html += '<div class="change-section removed"><h3>❌ 下架房源</h3><ul>'
            for unit in changes['removed']:
                changes_html += f"<li><strong>{unit['display_unit']}</strong> - {unit['floor_plan']} - {unit['display_price']}</li>"
            changes_html += '</ul></div>'
            
        if changes['price_changed']:
            changes_html += '<div class="change-section price-changed"><h3>💰 价格变动</h3><ul>'
            for item in changes['price_changed']:
                changes_html += f"<li>{item['desc']}</li>"
            changes_html += '</ul></div>'
            
        if changes['date_changed']:
            changes_html += '<div class="change-section date-changed"><h3>📅 日期变动</h3><ul>'
            for item in changes['date_changed']:
                item_unit = item['unit']
                changes_html += f"<li><strong>{item_unit['display_unit']}</strong>: {item['old_date']} -> {item['new_date']}</li>"
            changes_html += '</ul></div>'
            
        changes_html += '</div>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>RentMiro 公寓监控</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .header a {{ color: white; text-decoration: none; }}
            .header a:hover {{ text-decoration: underline; }}
            .summary {{ background: #ecf0f1; padding: 15px; margin-bottom: 20px; border-radius: 0 0 8px 8px; }}
            
            /* Changes Section */
            .changes-container {{ margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .change-section {{ padding: 15px; border-radius: 8px; border: 1px solid #ddd; }}
            .change-section h3 {{ margin-top: 0; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 10px; }}
            .change-section ul {{ padding-left: 20px; margin-bottom: 0; }}
            .change-section li {{ margin-bottom: 5px; }}
            
            .added {{ background-color: #e8f5e9; border-color: #a5d6a7; color: #2e7d32; }}
            .removed {{ background-color: #ffebee; border-color: #ef9a9a; color: #c62828; }}
            .price-changed {{ background-color: #fff8e1; border-color: #ffe082; color: #f57f17; }}
            .date-changed {{ background-color: #e3f2fd; border-color: #90caf9; color: #1565c0; }}
            
            /* Controls */
            .controls {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }}
            .control-group {{ display: flex; align-items: center; gap: 10px; margin-right: 20px; }}
            select, input {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; vertical-align: middle; }}
            th {{ background-color: #f8f9fa; font-weight: 600; color: #2c3e50; position: sticky; top: 0; }}
            tr:hover {{ background-color: #f5f5f5; }}
            
            .price {{ font-weight: bold; }}
            .price-up {{ color: #e74c3c; }}
            .price-down {{ color: #27ae60; }}
            .price-same {{ color: #2c3e50; }}
            
            .unit-badge {{ background: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; display: inline-block; }}
            .new-badge {{ background: #2ecc71; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 5px; }}
            
            .floor-plan-img {{ width: 100px; height: auto; border-radius: 4px; cursor: pointer; transition: transform 0.2s; }}
            .floor-plan-img:hover {{ transform: scale(2.5); z-index: 100; position: relative; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
            
            .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
        </style>
        <script>
            function filterTable() {{
                // Get selected beds
                const bedCheckboxes = document.querySelectorAll('input[name="bedFilter"]:checked');
                const selectedBeds = Array.from(bedCheckboxes).map(cb => cb.value);
                
                const priceFilter = document.getElementById('priceFilter').value;
                const dateFilter = document.getElementById('dateFilter').value;
                const rows = document.querySelectorAll('tbody tr');
                
                rows.forEach(row => {{
                    const beds = row.getAttribute('data-beds');
                    const price = parseInt(row.getAttribute('data-price'));
                    const availableDate = row.getAttribute('data-available');
                    
                    let show = true;
                    
                    // Bed filter (if any selected)
                    if (selectedBeds.length > 0 && !selectedBeds.includes(beds)) {{
                        show = false;
                    }}
                    
                    // Price filter
                    if (priceFilter && price > parseInt(priceFilter)) {{
                        show = false;
                    }}
                    
                    // Date filter (Move-in date)
                    // Logic: If I want to move in on X, the unit must be available on or before X.
                    if (dateFilter) {{
                        if (availableDate > dateFilter) {{
                            show = false;
                        }}
                    }}
                    
                    row.style.display = show ? '' : 'none';
                }});
                
                // Update count
                const visibleCount = Array.from(rows).filter(r => r.style.display !== 'none').length;
                document.getElementById('visibleCount').textContent = visibleCount;
            }}
            
            // Set default date to empty (show all)
            window.onload = function() {{
                // const today = new Date().toISOString().split('T')[0];
                // document.getElementById('dateFilter').value = today;
                filterTable();
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1 style="margin:0"><a href="https://www.rentmiro.com/floorplans" target="_blank" style="color:white; text-decoration:none;">RentMiro 公寓监控 🔗</a></h1>
                    <a href="../../index.html" style="color:white; text-decoration:none; background:rgba(255,255,255,0.2); padding:5px 10px; border-radius:4px; font-size:0.9em;">🏠 返回首页</a>
                </div>
                <p style="margin:10px 0 0 0; opacity: 0.8">更新时间: {data.get('timestamp')}</p>
            </div>
            
            <div class="summary">
                <strong>当前可用房源:</strong> {data.get('total_units')} 套
            </div>
            
            {changes_html}
            
            <div class="controls">
                <div class="control-group">
                    <label>户型筛选:</label>
                    <div style="display: flex; gap: 10px; background: white; padding: 5px 10px; border: 1px solid #ddd; border-radius: 4px;">
                        <label><input type="checkbox" name="bedFilter" value="0" onchange="filterTable()"> Studio</label>
                        <label><input type="checkbox" name="bedFilter" value="1" onchange="filterTable()"> 1B</label>
                        <label><input type="checkbox" name="bedFilter" value="2" onchange="filterTable()"> 2B</label>
                        <label><input type="checkbox" name="bedFilter" value="3" onchange="filterTable()"> 3B</label>
                    </div>
                </div>
                <div class="control-group">
                    <label>最高价格:</label>
                    <input type="number" id="priceFilter" placeholder="输入最高预算" onkeyup="filterTable()" style="width: 100px;">
                </div>
                <div class="control-group">
                    <label>期望入住日期:</label>
                    <input type="date" id="dateFilter" onchange="filterTable()">
                </div>
                <div class="control-group" style="margin-left: auto; color: #666;">
                    显示: <span id="visibleCount">{len(data.get('units', []))}</span> / {len(data.get('units', []))}
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>房间号</th>
                        <th>户型</th>
                        <th>户型图</th>
                        <th>面积 (sq.ft)</th>
                        <th>价格</th>
                        <th>可用时间</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for unit in data.get('units', []):
        # Determine price class and arrow
        price_class = "price-same"
        price_arrow = ""
        change = unit.get('price_change', 0)
        
        if change > 0:
            price_class = "price-up"
            price_arrow = f" <span style='font-size:0.8em'>▲{change}</span>"
        elif change < 0:
            price_class = "price-down"
            price_arrow = f" <span style='font-size:0.8em'>▼{abs(change)}</span>"
            
        new_badge = '<span class="new-badge">NEW</span>' if unit.get('is_new') else ''
        
        # Floor plan image
        img_html = f'<img src="{unit.get("floor_plan_image")}" class="floor-plan-img" loading="lazy" alt="Floor Plan">' if unit.get("floor_plan_image") else '<span style="color:#ccc">无图</span>'
        
        html_content += f"""
                    <tr data-beds="{unit.get('beds')}" data-price="{unit.get('price')}" data-available="{unit.get('available_on')}">
                        <td>
                            <span class="unit-badge">{unit.get('display_unit')}</span>
                            {new_badge}
                        </td>
                        <td>
                            <strong>{unit.get('floor_plan')}</strong><br>
                            <span style="color:#666; font-size:0.9em">{unit.get('beds')}B{unit.get('baths')}B</span>
                        </td>
                        <td>{img_html}</td>
                        <td>{unit.get('area')}</td>
                        <td class="{price_class}">
                            {unit.get('display_price')}
                            {price_arrow}
                        </td>
                        <td>{unit.get('available_on')}</td>
                    </tr>
        """
        
    html_content += """
                </tbody>
            </table>
            
            <div class="footer">
                Generated by RentMiro Scraper
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('./modules/rentmiro/data.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ HTML报告已生成: data.html")

if __name__ == "__main__":
    data, status = scrape_rentmiro_data()
    save_data(data, status)
