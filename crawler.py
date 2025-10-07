import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_session():
    """創建一個配置好的 requests session"""
    session = requests.Session()
    
    # 設定重試策略
    retry_strategy = Retry(
        total=3,  # 總重試次數
        backoff_factor=1,  # 退避因子
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重試的HTTP狀態碼
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # 允許重試的HTTP方法
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 設定 headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    return session

def make_request_with_retry(session, url, max_retries=3, base_timeout=10):
    """發送請求並處理重試邏輯"""
    for attempt in range(max_retries):
        try:
            # 計算當前嘗試的超時時間（指數退避）
            timeout = base_timeout * (2 ** attempt)
            
            logger.info(f"嘗試第 {attempt + 1} 次請求 {url} (超時: {timeout}秒)")
            
            response = session.get(url, timeout=timeout)
            response.raise_for_status()  # 檢查HTTP錯誤
            return response
            
        except requests.exceptions.Timeout:
            logger.warning(f"第 {attempt + 1} 次請求超時")
            if attempt < max_retries - 1:
                wait_time = random.uniform(1, 3) * (attempt + 1)
                logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                time.sleep(wait_time)
            
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"第 {attempt + 1} 次連接錯誤: {e}")
            if attempt < max_retries - 1:
                wait_time = random.uniform(2, 5) * (attempt + 1)
                logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                time.sleep(wait_time)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"第 {attempt + 1} 次請求發生錯誤: {e}")
            if attempt < max_retries - 1:
                wait_time = random.uniform(1, 3) * (attempt + 1)
                logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                time.sleep(wait_time)
    
    # 所有重試都失敗
    raise requests.exceptions.RequestException(f"經過 {max_retries} 次重試後仍無法連接到 {url}")

def get_activity_details(session, activity_url):
    """獲取活動詳細資訊，包括圖片"""
    try:
        response = make_request_with_retry(session, activity_url, max_retries=2, base_timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        
        # 尋找活動圖片
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # 只收集上傳的活動圖片
            if 'upload/event/' in src:
                if src.startswith('/'):
                    full_url = f"https://yilanart.ilccb.gov.tw{src}"
                elif not src.startswith('http'):
                    full_url = f"https://yilanart.ilccb.gov.tw/{src}"
                else:
                    full_url = src
                
                images.append({
                    'url': full_url,
                    'alt': alt or '活動圖片'
                })
        
        details['images'] = images
        
        # 嘗試獲取更詳細的活動描述
        content_div = soup.find('div', class_='content')
        if content_div:
            # 尋找活動描述文字
            text_elements = content_div.find_all(['p', 'div'], string=True)
            description_parts = []
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if len(text) > 20 and '活動' in text:  # 可能是活動描述
                    description_parts.append(text)
            
            if description_parts:
                details['description'] = ' '.join(description_parts[:2])  # 取前兩段
        
        return details
        
    except Exception as e:
        logger.warning(f"獲取活動詳情失敗 {activity_url}: {e}")
        return {'images': [], 'description': ''}

def crawl_yilan_activities():
    """爬取宜蘭縣文化局活動資訊"""
    url = "https://yilanart.ilccb.gov.tw/index.php?inter=activity"
    
    try:
        logger.info(f"開始爬取: {url}")
        
        # 使用新的 session 創建函數
        session = create_session()
        
        # 忽略 SSL 憑證驗證問題
        session.verify = False
        
        # 禁用 SSL 警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 使用新的重試請求函數
        response = make_request_with_retry(session, url, max_retries=3, base_timeout=10)
        
        # 設定正確的編碼
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.info("成功取得網頁內容")
        
        activities = []
        
        # 根據實際網頁結構調整選擇器
        # 找到 content div
        content_div = soup.find('div', class_='content')
        
        if content_div:
            # 尋找活動連結，排除導航連結
            activity_links = content_div.find_all('a', href=True)
            
            for link in activity_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 只處理活動詳情連結（包含 did= 參數的連結）
                if 'did=' in href and text:
                    try:
                        activity = {}
                        
                        # 解析活動文字，格式通常是：分類日期標題地點
                        import re
                        
                        # 提取活動標題（最後的文字部分）
                        # 分割文字，嘗試找到模式
                        parts = text.split('免票入場') if '免票入場' in text else text.split('線上購票') if '線上購票' in text else [text]
                        
                        if len(parts) >= 2:
                            # 有票價資訊
                            activity['title'] = parts[0].strip()
                            activity['price'] = '免票入場' if '免票入場' in text else '線上購票' if '線上購票' in text else '未知'
                            activity['location'] = parts[1].strip() if len(parts) > 1 else ''
                        else:
                            # 沒有明確的票價資訊，嘗試其他分割方式
                            activity['title'] = text
                            activity['price'] = '未知'
                            activity['location'] = ''
                        
                        # 嘗試從標題中提取日期
                        date_pattern = r'(\d{4})(\d{2})\.(\d{2})\.([A-Za-z]{3})'
                        date_match = re.search(date_pattern, text)
                        if date_match:
                            year, month, day, day_name = date_match.groups()
                            activity['date'] = f"{year}-{month}-{day} ({day_name})"
                            # 清理標題，移除日期部分
                            activity['title'] = re.sub(date_pattern, '', activity['title']).strip()
                        
                        # 提取活動類型（如果文字開頭有分類）
                        category_match = re.match(r'^(展覽|表演|研習|故事|活動)', text)
                        if category_match:
                            activity['category'] = category_match.group(1)
                            # 從標題中移除分類
                            activity['title'] = re.sub(r'^(展覽|表演|研習|故事|活動)', '', activity['title']).strip()
                        
                        # 建構完整的活動連結
                        if href.startswith('/'):
                            activity['url'] = f"https://yilanart.ilccb.gov.tw{href}"
                        elif not href.startswith('http'):
                            activity['url'] = f"https://yilanart.ilccb.gov.tw/{href}"
                        else:
                            activity['url'] = href
                        
                        # 獲取活動詳細資訊（包括圖片）
                        logger.info(f"獲取活動詳情: {activity.get('title', '未知活動')}")
                        details = get_activity_details(session, activity['url'])
                        activity.update(details)
                        
                        # 添加爬取時間
                        activity['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 清理標題中的多餘內容
                        if activity.get('title'):
                            title = activity['title']
                            # 移除可能的地點資訊（如果在標題末尾）
                            locations = ['宜蘭文學館', '宜蘭美術館', '中興文化創意園區', '頭城親子館', 
                                       '宜蘭演藝廳', '羅東文化工場', '羅東鎮圖仁愛館', '化龍一村', '其他地點']
                            for loc in locations:
                                if title.endswith(loc):
                                    title = title[:-len(loc)].strip()
                                    if not activity['location']:
                                        activity['location'] = loc
                            activity['title'] = title
                        
                        # 只有標題不為空才加入
                        if activity.get('title') and len(activity['title']) > 3:
                            activities.append(activity)
                            
                    except Exception as e:
                        logger.warning(f"解析單個活動時發生錯誤: {e}")
                        continue
        else:
            logger.warning("未找到活動內容區域")
        
        # 儲存結果
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        
        # 儲存為 JSON
        json_file = f'{output_dir}/yilan_activities_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(activities, f, ensure_ascii=False, indent=2)
        
        # 儲存最新資料 (覆蓋式)
        latest_file = f'{output_dir}/latest_activities.json'
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump({
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_count': len(activities),
                'activities': activities
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功爬取 {len(activities)} 筆活動資料")
        logger.info(f"資料已儲存至: {json_file}")
        
        return activities
        
    except requests.RequestException as e:
        logger.error(f"網路請求錯誤: {e}")
        raise
    except Exception as e:
        logger.error(f"爬取過程發生錯誤: {e}")
        raise

def generate_readme():
    """生成 README 文件顯示最新資料"""
    try:
        with open('data/latest_activities.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        readme_content = f"""# 宜蘭縣文化局活動資訊

## 📊 最新更新資訊
- **更新時間**: {data['update_time']}
- **活動數量**: {data['total_count']} 筆

## 🎭 近期活動

"""
        
        for i, activity in enumerate(data['activities'][:10], 1):  # 只顯示前10筆
            readme_content += f"### {i}. {activity.get('title', '無標題')}\n"
            if activity.get('date'):
                readme_content += f"- **時間**: {activity['date']}\n"
            if activity.get('location'):
                readme_content += f"- **地點**: {activity['location']}\n"
            if activity.get('category'):
                readme_content += f"- **類型**: {activity['category']}\n"
            if activity.get('price'):
                readme_content += f"- **票價**: {activity['price']}\n"
            if activity.get('url'):
                readme_content += f"- **連結**: [{activity['url']}]({activity['url']})\n"
            
            # 添加圖片
            if activity.get('images') and len(activity['images']) > 0:
                readme_content += f"- **圖片**:\n"
                for img in activity['images'][:2]:  # 最多顯示2張圖片
                    readme_content += f"  - ![{img.get('alt', '活動圖片')}]({img['url']})\n"
            
            readme_content += "\n"
        
        readme_content += f"""
## 📁 資料檔案
- [最新活動資料 (JSON)](./data/latest_activities.json)
- [歷史資料目錄](./data/)

## 🤖 自動化說明
此專案使用 GitHub Actions 每天自動爬取2次資料 (09:00 和 21:00 UTC+8)

---
*最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info("README.md 已更新")
        
    except Exception as e:
        logger.warning(f"生成 README 時發生錯誤: {e}")

def create_fallback_data():
    """創建備用資料檔案，當爬取失敗時使用"""
    fallback_data = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': 0,
        'activities': [],
        'status': 'failed',
        'message': '無法連接到宜蘭文化局網站，請稍後再試'
    }
    
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 只有在沒有任何資料時才創建備用檔案
    latest_file = f'{output_dir}/latest_activities.json'
    if not os.path.exists(latest_file):
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=2)
        logger.info("已創建備用資料檔案")
    
    return fallback_data

if __name__ == "__main__":
    success = False
    activities = []
    
    try:
        activities = crawl_yilan_activities()
        generate_readme()
        success = True
        
        print(f"✅ 爬取完成，共 {len(activities)} 筆活動資料")
        
        # 顯示前3筆資料作為預覽
        for i, activity in enumerate(activities[:3], 1):
            print(f"\n{i}. {activity.get('title', '無標題')}")
            if activity.get('date'):
                print(f"   時間: {activity['date']}")
            if activity.get('location'):
                print(f"   地點: {activity['location']}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"網路連線問題: {e}")
        print(f"⚠️ 網路連線失敗，這可能是暫時性問題")
        print("建議稍後再試，或檢查網站是否正常運作")
        
        # 創建備用資料
        fallback_data = create_fallback_data()
        
        # GitHub Actions 環境下不要直接失敗，而是提供有用的資訊
        if os.getenv('GITHUB_ACTIONS'):
            print("🔄 這是 GitHub Actions 環境，將繼續執行而不中斷工作流程")
            print(f"📝 下次排程執行時間會自動重試")
            exit(0)  # 不讓 GitHub Actions 失敗
        else:
            exit(1)  # 本地執行時顯示錯誤
            
    except Exception as e:
        logger.error(f"意外錯誤: {e}")
        print(f"❌ 執行失敗: {e}")
        
        # 創建備用資料
        fallback_data = create_fallback_data()
        
        # GitHub Actions 環境下提供更多資訊
        if os.getenv('GITHUB_ACTIONS'):
            print("🔄 這是 GitHub Actions 環境")
            print(f"📝 錯誤詳情已記錄，下次排程執行時會自動重試")
            exit(0)  # 不讓 GitHub Actions 失敗
        else:
            exit(1)  # 本地執行時顯示錯誤