import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape_99_data_enhanced():
    """增强版99.com数据抓取器，尝试多种方式获取数据"""
    base_url = "https://hd.99.com/jz/qxhd/"
    api_url = "https://hd.99.com/jz/qxhd/?r=/Index/loadPageData"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Referer': base_url,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 首先尝试直接调用API
        print("尝试调用API获取数据...")
        api_res = requests.get(api_url, headers=headers, timeout=30)
        
        if api_res.status_code == 200:
            try:
                api_data = api_res.json()
                if api_data and 'info' in api_data and api_data['info']:
                    print(f"API调用成功，获取到 {len(api_data['info'])} 条记录")
                    return parse_api_data(api_data), 200
            except json.JSONDecodeError:
                print("API返回的不是有效JSON格式")
        
        # 如果API调用失败，尝试解析HTML页面
        print("API调用失败，尝试解析HTML页面...")
        page_res = requests.get(base_url, headers=headers, timeout=30)
        page_res.raise_for_status()
        
        soup = BeautifulSoup(page_res.text, 'html.parser')
        
        # 查找表格数据
        tables = soup.find_all('table')
        data = []
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    # 检查是否有正确的class
                    if any('number' in str(cell.get('class', [])) for cell in cells):
                        row_data = {
                            'number': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'fwq': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'player': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'hkzs': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                        }
                        data.append(row_data)
        
        # 如果没有找到表格，尝试从JavaScript中提取
        if not data:
            print("未找到表格数据，尝试从JavaScript中提取...")
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'loadPageData' in script.string:
                    js_content = script.string
                    # 尝试模拟JavaScript执行
                    data = extract_data_from_js(js_content)
                    if data:
                        break
        
        # 添加时间戳
        result = {
            'timestamp': datetime.now().isoformat(),
            'url': base_url,
            'api_url': api_url,
            'data': data,
            'total_records': len(data),
            'method': 'html_parsing'
        }
        
        return result, page_res.status_code
        
    except requests.RequestException as e:
        return {'error': str(e), 'timestamp': datetime.now().isoformat()}, 500
    except Exception as e:
        return {'error': str(e), 'timestamp': datetime.now().isoformat()}, 500


def parse_api_data(api_data):
    """解析API返回的数据"""
    data = []
    if 'info' in api_data and api_data['info']:
        for item in api_data['info']:
            row_data = {
                'number': str(item.get('rank', '')),
                'fwq': item.get('server_name', ''),
                'player': item.get('user_name', ''),
                'hkzs': str(item.get('rank_flower', ''))
            }
            data.append(row_data)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'url': 'https://hd.99.com/jz/qxhd/',
        'api_url': 'https://hd.99.com/jz/qxhd/?r=/Index/loadPageData',
        'data': data,
        'total_records': len(data),
        'method': 'api_call'
    }
    
    return result


def extract_data_from_js(js_content):
    """从JavaScript代码中提取数据"""
    # 这里可以实现更复杂的JavaScript解析逻辑
    # 目前返回空列表，表示需要进一步开发
    return []


def get_previous_data():
    """获取之前的数据用于比较"""
    try:
        # 检查是否存在备份文件（保存新数据前的旧数据）
        if os.path.exists('./modules/99/data.json.backup'):
            with open('./modules/99/data.json.backup', 'r', encoding='utf-8') as f:
                return json.load(f)
        # 如果没有备份文件，检查当前文件
        elif os.path.exists('./modules/99/data.json'):
            with open('./modules/99/data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None


def analyze_changes(current_data, previous_data):
    """分析数据变化，返回变化信息"""
    if not previous_data or 'data' not in previous_data:
        return "首次抓取数据，无法比较变化"
    
    changes = []
    current_players = {item['player']: int(item['hkzs']) for item in current_data['data']}
    previous_players = {item['player']: int(item['hkzs']) for item in previous_data['data']}
    
    # 检查现有玩家的变化
    for player in current_players:
        if player in previous_players:
            current_value = current_players[player]
            previous_value = previous_players[player]
            if current_value != previous_value:
                diff = current_value - previous_value
                change_symbol = "+" if diff > 0 else ""
                changes.append(f"{player}: {change_symbol}{diff}")
    
    # 检查新增的玩家
    for player in current_players:
        if player not in previous_players:
            changes.append(f"{player}: +{current_players[player]} (新增)")
    
    # 检查移除的玩家
    for player in previous_players:
        if player not in current_players:
            changes.append(f"{player}: -{previous_players[player]} (移除)")
    
    if not changes:
        return "数据无变化"
    
    return "变化详情:\n" + "\n".join(changes)


def has_data_changed(new_data):
    """检查数据是否真的发生了变化"""
    try:
        if os.path.exists('./modules/99/data.json'):
            with open('./modules/99/data.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 比较关键数据字段
            if old_data.get('total_records') != new_data.get('total_records'):
                return True
            
            # 比较玩家数据
            old_players = {item['player']: item['hkzs'] for item in old_data.get('data', [])}
            new_players = {item['player']: item['hkzs'] for item in new_data.get('data', [])}
            
            return old_players != new_players
        return True  # 文件不存在，认为有变化
    except Exception as e:
        print(f"检查数据变化时出错: {e}")
        return True  # 出错时认为有变化


def save_data(data, status_code):
    """保存数据到文件"""
    if status_code == 200:
        print("=== 开始保存数据流程 ===")
        
        # 先检查数据是否真的变化了
        if has_data_changed(data):
            print("📊 检测到数据变化，开始保存文件...")
            
            # 1. 检查并备份：如果存在旧数据，将其变为backup
            if os.path.exists('./modules/99/data.json'):
                print("发现现有 data.json，准备备份...")
                try:
                    import shutil
                    shutil.copy2('./modules/99/data.json', './modules/99/data.json.backup')
                    print("✅ 已备份旧数据到 data.json.backup")
                except Exception as e:
                    print(f"❌ 备份旧数据失败: {e}")
            else:
                print("📝 首次运行，没有现有数据需要备份")
            
            # 2. 获取历史数据用于对比（在保存新数据之前）
            print("正在获取历史数据用于对比...")
            previous_data = get_previous_data()
            if previous_data:
                print("📊 找到历史数据，将用于对比分析")
            else:
                print("🆕 没有历史数据，这是首次抓取")
            
            # 3. 拉取最新数据：保存新数据作为 data.json
            print("正在保存新数据...")
            with open('./modules/99/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 新数据已保存到 data.json，共 {data.get('total_records', 0)} 条记录")
            
            # 4. 对比分析：将新数据与历史数据做对比
            print("正在分析数据变化...")
            changes_info = analyze_changes(data, previous_data)
            print(f"📈 变化信息: {changes_info}")
            
            # 5. 生成邮件：创建包含变化分析的 data.html
            print("正在生成邮件HTML...")
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>99.com 数据抓取结果</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background: #f5f7fa; color: #333; }
                    .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
                    .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; display: flex; justify-content: space-between; align-items: center; }
                    .header h1 { margin: 0; font-size: 1.5em; }
                    .header a { color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 4px; font-size: 0.9em; }
                    
                    table { border-collapse: collapse; width: 100%; margin-top: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); background: white; }
                    th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f8f9fa; font-weight: 600; color: #2c3e50; }
                    tr:hover { background-color: #f5f5f5; }
                    
                    .summary { background-color: white; padding: 20px; border-radius: 0 0 8px 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                    .timestamp { color: #666; font-size: 14px; margin-bottom: 10px; }
                    .changes { background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 5px solid #ffc107; }
                    .changes pre { margin: 0; white-space: pre-wrap; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>99.com 数据抓取结果</h1>
                        <a href="../../index.html">🏠 返回首页</a>
                    </div>
                    <div class="summary">
                        <div class="timestamp">抓取时间: {data.get('timestamp', 'N/A')}</div>
                        <div>
                            <strong>总记录数:</strong> {data.get('total_records', 0)}<br>
                            <strong>数据源:</strong> {data.get('url', 'N/A')}<br>
                            <strong>抓取方式:</strong> {data.get('method', 'N/A')}
                        </div>
                    </div>
            """
            
            if data.get('data'):
                html_content += """
                <table>
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>服务器</th>
                            <th>玩家</th>
                            <th>花数量</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for i, record in enumerate(data['data'], 1):
                    html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{record.get('fwq', '')}</td>
                            <td>{record.get('player', '')}</td>
                            <td>{record.get('hkzs', '')}</td>
                        </tr>
                    """
                
                html_content += """
                    </tbody>
                </table>
                """
            else:
                html_content += "<p>未找到数据或出现错误</p>"
            
            # 添加变化信息
            html_content += f"""
            <div class="changes">
                <strong>📊 数据变化分析</strong>
                <pre>{changes_info}</pre>
            </div>
            """
            
            html_content += """
            </body>
            </html>
            """
            
            with open('./modules/99/data.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("✅ 邮件HTML已生成: data.html")
            
            # 6. 清理backup：删除 data.json.backup，为下次运行做准备
            if os.path.exists('./modules/99/data.json.backup'):
                try:
                    os.remove('./modules/99/data.json.backup')
                    print("🗑️ 已清理 backup 文件: data.json.backup")
                except Exception as e:
                    print(f"❌ 清理 backup 文件失败: {e}")
            else:
                print("📝 没有backup文件需要清理")
            
            print("=== 数据保存流程完成 ===")
        else:
            print("📊 数据无变化，跳过文件保存")
            print("=== 数据保存流程完成（无变化） ===")
        
    else:
        print(f"❌ 抓取失败，状态码: {status_code}")
        if 'error' in data:
            print(f"错误信息: {data['error']}")


if __name__ == "__main__":
    data, status_code = scrape_99_data_enhanced()
    save_data(data, status_code)
