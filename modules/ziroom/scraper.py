import os, re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def query(uri, keyword):
    if not uri:
        print("URI environment variable not set")
        return None, []
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    
    try:
        res = requests.get(uri, headers=headers)
        if res.status_code != 200:
            print(f"Failed to fetch data: {res.status_code}")
            return res, []
            
        soup = BeautifulSoup(res.text, 'html.parser')
        # Find all h5 with class 'title sign'
        houses = soup.find_all('h5', attrs={'class': 'title sign'})
        
        # Filter by keyword if provided
        if keyword:
            filtered_houses = [h for h in houses if h.string and keyword in h.string]
            return res, filtered_houses
        else:
            return res, houses
            
    except Exception as e:
        print(f"Error querying ziroom: {e}")
        return None, []

def generate_html(houses, uri):
    timestamp = datetime.now().isoformat()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ziroom Monitor Result</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background: #f5f7fa; color: #333; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; font-size: 1.5em; }}
            .header a {{ color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 4px; font-size: 0.9em; }}
            
            .summary {{ background-color: white; padding: 20px; border-radius: 0 0 8px 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .timestamp {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
            
            .house-list {{ list-style: none; padding: 0; }}
            .house-item {{ background: white; margin-bottom: 10px; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s; }}
            .house-item:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .house-item a {{ text-decoration: none; color: #2c3e50; font-weight: bold; font-size: 1.1em; display: block; }}
            .house-item a:hover {{ color: #3498db; }}
            
            .empty-state {{ text-align: center; padding: 40px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Ziroom 房源监控</h1>
                <a href="../../index.html">🏠 返回首页</a>
            </div>
            
            <div class="summary">
                <div class="timestamp">更新时间: {timestamp}</div>
                <div>
                    <strong>监控链接:</strong> <a href="{uri}" target="_blank" style="color:#3498db; text-decoration:none;">{uri}</a><br>
                    <strong>找到房源:</strong> {len(houses)} 套
                </div>
            </div>
            
            {generate_list(houses)}
            
        </div>
    </body>
    </html>
    """
    return html_content

def generate_list(houses):
    if not houses:
        return '<div class="empty-state">没有找到符合条件的房源</div>'
        
    items = []
    for h in houses:
        # Extract link and text
        # h is an h5 tag, usually contains an 'a' tag
        link = h.find('a')
        if link:
            href = link.get('href', '#')
            if href.startswith('//'):
                href = 'https:' + href
            text = link.get_text(strip=True)
            items.append(f'<li class="house-item"><a href="{href}" target="_blank">{text}</a></li>')
        else:
            items.append(f'<li class="house-item">{h.get_text(strip=True)}</li>')
            
    return f'<ul class="house-list">{"".join(items)}</ul>'

if __name__ == "__main__":
    uri = os.environ.get('URI')
    keyword = os.environ.get('KEYWORD')
    
    res, houses = query(uri, keyword)
    
    if res and res.status_code == 200:
        html = generate_html(houses, uri)
        with open('modules/ziroom/data.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Successfully generated data.html with {len(houses)} items")
    else:
        print("Failed to generate report")
