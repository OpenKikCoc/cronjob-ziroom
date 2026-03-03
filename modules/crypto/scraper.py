import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from duckduckgo_search import DDGS

def search_ddg(query, max_results=10):
    """Search DuckDuckGo for query"""
    print(f"Searching DDG for: {query}")
    results = []
    try:
        with DDGS() as ddgs:
            ddg_results = ddgs.text(query, max_results=max_results)
            for r in ddg_results:
                results.append({
                    'title': r['title'],
                    'url': r['href'],
                    'description': r['body'],
                    'source': 'DuckDuckGo',
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'strategy': 'Search Result',
                    'quantity': 'Unknown',
                    'end_date': 'Unknown'
                })
    except Exception as e:
        print(f"Error searching DDG: {e}")
    print(f"  Total DDG results for '{query}': {len(results)}")
    return results

def scrape_airdrops_io_search(query):
    """Scrape airdrops.io search results for specific query"""
    print(f"Scraping airdrops.io search for: {query}")
    url = f"https://airdrops.io/?s={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        articles = soup.find_all('article')
        print(f"  Found {len(articles)} articles for query '{query}'")
        
        for article in articles:
            title_tag = article.find('h2', class_='entry-title')
            if not title_tag or not title_tag.a:
                continue
                
            title = title_tag.a.text.strip()
            link = title_tag.a['href']
            
            # Get description
            desc = ""
            desc_tag = article.find('div', class_='entry-content')
            if desc_tag:
                desc = desc_tag.text.strip()
                
            # Fetch details
            strategy = "Check website for details."
            quantity = "Unknown"
            end_date = "Unknown"
            
            try:
                # Reuse the detail fetching logic if possible, or just keep it simple for search results
                # Let's do a quick fetch
                res_detail = requests.get(link, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                
                # Extract Strategy
                guide_list = soup_detail.find('ul', class_='list-steps')
                if guide_list:
                    steps = [li.get_text(strip=True) for li in guide_list.find_all('li')]
                    strategy = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])
                    
            except:
                pass

            results.append({
                'title': title,
                'url': link,
                'description': desc,
                'source': 'airdrops.io',
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy,
                'quantity': quantity,
                'end_date': end_date
            })
            time.sleep(1)
            
    except Exception as e:
        print(f"Error scraping airdrops.io search: {e}")
    return results

def scrape_airdrops_io_latest():
    """Scrape airdrops.io latest airdrops with details"""
    print(f"Scraping airdrops.io latest...")
    url = "https://airdrops.io/latest/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        articles = soup.find_all('article')
        print(f"  Found {len(articles)} articles on airdrops.io/latest")
        
        for i, article in enumerate(articles):
            # Skip header article if it doesn't look like an airdrop
            if 'type-page' in article.get('class', []):
                continue

            title_tag = article.find('h2') or article.find('h3')
            if not title_tag:
                continue
                
            link_tag = article.find('a')
            if not link_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            
            # Get basic description
            desc = ""
            content_div = article.find('div', class_='entry-content')
            if content_div:
                desc = content_div.get_text(strip=True)
            
            # Fetch details page for more info
            try:
                print(f"    Fetching details for: {title}")
                res_detail = requests.get(link, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                
                # Extract Strategy (Guide)
                strategy = "Check website for details."
                guide_list = soup_detail.find('ul', class_='list-steps')
                if not guide_list:
                    # Try finding "Step-by-Step Guide" text and getting the next list
                    guide_header = soup_detail.find(string=lambda text: text and "Step-by-Step Guide" in text)
                    if guide_header:
                        parent = guide_header.find_parent()
                        if parent:
                            next_ul = parent.find_next('ul')
                            if next_ul:
                                guide_list = next_ul
                
                if guide_list:
                    steps = [li.get_text(strip=True) for li in guide_list.find_all('li')]
                    strategy = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])
                
                # Extract Metadata (Value, End Date)
                quantity = "Unknown"
                end_date = "Unknown"
                
                # Look for metadata list
                meta_list = soup_detail.find('ul', class_='airdrop-meta')
                if meta_list:
                    for li in meta_list.find_all('li'):
                        text = li.get_text(strip=True)
                        if "Value:" in text:
                            quantity = text.replace("Value:", "").strip()
                        elif "End Date:" in text:
                            end_date = text.replace("End Date:", "").strip()
                
            except Exception as e:
                print(f"    Error fetching details for {title}: {e}")
                strategy = "Failed to fetch details."
                quantity = "Unknown"
                end_date = "Unknown"

            results.append({
                'title': title,
                'url': link,
                'description': desc,
                'source': 'airdrops.io',
                'query': 'latest',
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy,
                'quantity': quantity,
                'end_date': end_date
            })
            
            # Be nice to the server
            time.sleep(1)
            
    except Exception as e:
        print(f"Error scraping airdrops.io: {e}")
    print(f"  Total airdrops.io results: {len(results)}")
    return results

def scrape_defillama_airdrops():
    """Scrape DefiLlama claimable airdrops via JSON"""
    print(f"Scraping DefiLlama airdrops...")
    url = "https://defillama.com/airdrops"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        script = soup.find('script', id='__NEXT_DATA__')
        if script:
            data = json.loads(script.string)
            pageProps = data.get('props', {}).get('pageProps', {})
            airdrops = pageProps.get('claimableAirdrops', [])
            
            print(f"  Found {len(airdrops)} claimable airdrops on DefiLlama")
            
            for ad in airdrops:
                title = ad.get('name', 'Unknown')
                link = ad.get('page', '')
                
                results.append({
                    'title': title,
                    'url': link,
                    'description': "Claimable airdrop found on DefiLlama.",
                    'source': 'DefiLlama',
                    'query': 'claimable',
                    'timestamp': datetime.now().isoformat(),
                    'strategy': "Visit the claim page.",
                    'quantity': "Unknown",
                    'end_date': "Unknown"
                })
        else:
            print("  Could not find __NEXT_DATA__ script on DefiLlama")
            
    except Exception as e:
        print(f"Error scraping DefiLlama: {e}")
    print(f"  Total DefiLlama results: {len(results)}")
    return results

def analyze_and_filter(items):
    """Filter and analyze items, keeping ONLY developer-relevant ones"""
    unique_items = {}
    
    # Required keywords (must have at least one)
    required_keywords = ['airdrop', 'claim', 'token', 'reward', 'incentive', 'devdrop']
    
    # Developer keywords (must have at least one)
    dev_keywords = [
        'github', 'developer', 'dev', 'commit', 'repo', 
        'testnet', 'node', 'validator', 'contract', 'hackathon', 
        'bounty', 'sdk', 'api', 'protocol', 'stack', 'layer 2', 'l2',
        'contributor', 'grant', 'technical'
    ]
    
    # Blacklist domains
    blacklist_domains = [
        'github.com', 'wikipedia.org', 'google.com', 'facebook.com', 
        'youtube.com', 'twitter.com', 'x.com', 'linkedin.com',
        'instagram.com', 'reddit.com'
    ]
    
    for item in items:
        url = item['url']
        
        # Check blacklist
        if any(domain in url for domain in blacklist_domains):
            # Exception for raw content or specific paths if needed, but generally skip main sites
            continue
            
        # Simple deduplication by URL
        if url in unique_items:
            continue
            
        # Check relevance
        text = (item['title'] + " " + item['description'] + " " + item.get('strategy', '')).lower()
        
        # Must have required keyword
        has_required = any(kw in text for kw in required_keywords)
        if not has_required:
            continue
            
        # Must have dev keyword
        matched_keywords = []
        for kw in dev_keywords:
            if kw in text:
                matched_keywords.append(kw)
        
        if not matched_keywords:
            continue
            
        # Calculate score based on number of matches
        relevance_score = len(matched_keywords)
        
        item['relevance_score'] = relevance_score
        item['matched_keywords'] = matched_keywords
        
        # Mark as potential scam if suspicious keywords found (very basic)
        scam_keywords = ['send eth', 'private key', 'seed phrase']
        is_suspicious = any(sk in text for sk in scam_keywords)
        item['is_suspicious'] = is_suspicious
        
        unique_items[url] = item
        
    # Convert back to list and sort by relevance
    sorted_items = sorted(unique_items.values(), key=lambda x: x['relevance_score'], reverse=True)
    return sorted_items

def save_data(data):
    """Save data to JSON and generate HTML"""
    print("=== Saving Data ===")
    
    # Save JSON
    os.makedirs('./modules/crypto', exist_ok=True)
    with open('./modules/crypto/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # Generate HTML
    generate_html(data)
    print("=== Data Saved ===")

def generate_html(data):
    """Generate HTML report"""
    items = data.get('items', [])
    timestamp = data.get('timestamp')
    
    # Since we filter strictly, all items are dev items
    dev_items = items
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>GitHub Developer Airdrop Monitor</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; color: #333; line-height: 1.6; background-color: #f4f6f8; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .header {{ background: #24292e; color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; font-size: 1.5em; }}
            .header a {{ color: white; text-decoration: none; }}
            
            .section-title {{ 
                margin: 30px 0 15px 0; 
                padding-bottom: 10px; 
                border-bottom: 2px solid #eee; 
                font-size: 1.5em; 
                color: #24292e; 
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .item {{ border: 1px solid #e1e4e8; padding: 20px; margin-bottom: 20px; border-radius: 6px; transition: all 0.2s; background: white; }}
            .item:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-color: #0366d6; }}
            
            .item-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }}
            .item-title {{ font-size: 1.4em; font-weight: 600; color: #0366d6; text-decoration: none; }}
            .item-title:hover {{ text-decoration: underline; }}
            
            .tags {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
            .tag {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500; }}
            .tag-source {{ background: #f1f8ff; color: #0366d6; border: 1px solid #c8e1ff; }}
            .tag-relevance {{ background: #fff5b1; color: #735c0f; border: 1px solid #f9e28b; }}
            .tag-suspicious {{ background: #ffeef0; color: #cb2431; border: 1px solid #fdaeb7; }}
            .tag-quantity {{ background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }}
            .tag-date {{ background: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb; }}
            
            .item-details {{ display: grid; grid-template-columns: 1fr; gap: 15px; margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }}
            @media (min-width: 768px) {{
                .item-details {{ grid-template-columns: 2fr 1fr; }}
            }}
            
            .detail-section h4 {{ margin: 0 0 8px 0; font-size: 0.95em; color: #586069; text-transform: uppercase; letter-spacing: 0.5px; }}
            .strategy-text {{ white-space: pre-line; font-size: 0.95em; color: #24292e; background: #f6f8fa; padding: 10px; border-radius: 4px; border: 1px solid #eaecef; }}
            
            .footer {{ margin-top: 30px; text-align: center; color: #586069; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 20px; }}
            
            .empty-state {{ padding: 30px; text-align: center; color: #586069; background: #f9f9f9; border-radius: 8px; border: 1px dashed #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>GitHub Developer Airdrop Monitor</h1>
                    <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Updated: {timestamp}</div>
                </div>
                <a href="../../index.html" style="background:rgba(255,255,255,0.2); padding:5px 10px; border-radius:4px; font-size:0.9em;">🏠 Home</a>
            </div>
            
            <div style="padding: 15px; background: #e6fffa; border: 1px solid #b2f5ea; border-radius: 6px; margin-bottom: 25px; color: #234e52;">
                <p style="margin: 0;">Found <strong>{len(items)}</strong> developer-focused opportunities.</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">⚠️ Disclaimer: Always do your own research (DYOR). Never share your private keys.</p>
            </div>
            
            <h2 class="section-title">🎯 Developer & GitHub Focused</h2>
            <div class="items">
    """
    
    def render_item(item):
        suspicious_html = '<span class="tag tag-suspicious">⚠️ Suspicious</span>' if item.get('is_suspicious') else ''
        relevance_html = f'<span class="tag tag-relevance">Score: {item["relevance_score"]}</span>' if item["relevance_score"] > 0 else ''
        quantity_html = f'<span class="tag tag-quantity">💰 {item.get("quantity", "Unknown")}</span>' if item.get("quantity") and item.get("quantity") != "Unknown" else ''
        date_html = f'<span class="tag tag-date">📅 End: {item.get("end_date", "Unknown")}</span>'
        
        strategy_content = item.get('strategy', 'No strategy provided.')
        if not strategy_content: strategy_content = "No strategy provided."
        
        description = item.get('description', '')
        if len(description) > 300: description = description[:300] + '...'
        
        # Highlight matched keywords in description
        if item.get('matched_keywords'):
            for kw in item['matched_keywords']:
                # Simple case-insensitive replace
                description = description.replace(kw, f"<strong>{kw}</strong>")
                description = description.replace(kw.capitalize(), f"<strong>{kw.capitalize()}</strong>")
        
        return f"""
                <div class="item">
                    <div class="item-header">
                        <a href="{item['url']}" target="_blank" class="item-title">{item['title']}</a>
                        <div class="tags">
                            <span class="tag tag-source">{item['source']}</span>
                            {relevance_html}
                            {quantity_html}
                            {date_html}
                            {suspicious_html}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px; color: #444;">
                        {description}
                    </div>
                    
                    <div class="item-details">
                        <div class="detail-section">
                            <h4>Strategy / Guide</h4>
                            <div class="strategy-text">{strategy_content}</div>
                        </div>
                        <div class="detail-section">
                            <h4>Details</h4>
                            <ul style="margin: 0; padding-left: 20px; font-size: 0.9em; color: #444;">
                                <li><strong>Source:</strong> {item['source']}</li>
                                <li><strong>Quantity:</strong> {item.get('quantity', 'Unknown')}</li>
                                <li><strong>End Date:</strong> {item.get('end_date', 'Unknown')}</li>
                                <li><strong>Query:</strong> {item.get('query', 'N/A')}</li>
                                <li><strong>Keywords:</strong> {', '.join(item.get('matched_keywords', []))}</li>
                            </ul>
                            <div style="margin-top: 15px;">
                                <a href="{item['url']}" target="_blank" style="display: block; text-align: center; background: #0366d6; color: white; padding: 8px; border-radius: 4px; text-decoration: none; font-weight: 500;">Visit Website</a>
                            </div>
                        </div>
                    </div>
                </div>
        """

    if dev_items:
        for item in dev_items:
            html_content += render_item(item)
    else:
        html_content += '<div class="empty-state">No specific developer airdrops found in this run.</div>'

    html_content += """
            </div>
            <div class="footer">
                Generated by Crypto Airdrop Scraper
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('./modules/crypto/data.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ HTML Report Generated: data.html")

def main():
    print("Starting Crypto Airdrop Scraper...")
    
    all_items = []
    
    # 1. Search DDG (Specific queries)
    queries = [
        '"airdrop" github contributors',
        '"claim" token github commit',
        '"devdrop" crypto'
    ]
    for q in queries:
        try:
            all_items.extend(search_ddg(q, max_results=2))
        except Exception as e:
            print(f"Skipping query {q} due to error: {e}")
        time.sleep(1)
        
    # 2. Scrape airdrops.io (Latest)
    # Reduced scope for speed
    # all_items.extend(scrape_airdrops_io_latest())
    
    # 2.1 Scrape airdrops.io (Search for github/developer)
    all_items.extend(scrape_airdrops_io_search("github"))
    # all_items.extend(scrape_airdrops_io_search("developer"))
    
    # 3. Scrape DefiLlama (Claimable)
    all_items.extend(scrape_defillama_airdrops())
    
    # 4. Analyze and Filter
    filtered_items = analyze_and_filter(all_items)
    
    # 5. Save
    data = {
        'timestamp': datetime.now().isoformat(),
        'items': filtered_items
    }
    
    save_data(data)

if __name__ == "__main__":
    main()
