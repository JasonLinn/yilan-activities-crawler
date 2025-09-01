# Claude AI 快速參考 - 宜蘭活動爬蟲

## 🚀 專案一覽

**專案類型**: Python 網頁爬蟲 + GitHub Actions 自動化  
**目標網站**: https://yilanart.ilccb.gov.tw/index.php?inter=activity  
**主要語言**: Python 3.9+  
**核心套件**: requests, beautifulsoup4  

## 📁 重要檔案

| 檔案 | 用途 | 修改頻率 |
|-----|------|----------|
| `crawler.py` | 主程式 | 高 |
| `requirements.txt` | 相依套件 | 低 |
| `.github/workflows/crawler.yml` | CI/CD | 中 |
| `DEVELOPMENT.md` | 開發指南 | 低 |
| `GUIDE.md` | 使用指南 | 低 |

## 🔧 核心函式

```python
# 主要爬取函式
def crawl_yilan_activities() -> list

# 獲取活動詳情（包含圖片）
def get_activity_details(session, activity_url) -> dict

# 生成展示頁面
def generate_readme() -> None
```

## 📊 資料流程

```
網站列表頁 → 提取活動連結 → 訪問詳情頁 → 提取圖片+資訊 → 儲存JSON → 生成README
```

## ⚠️ 重要注意事項

### SSL 問題
```python
session.verify = False  # 必須保持，目標網站憑證有問題
urllib3.disable_warnings()  # 禁用警告
```

### 編碼處理
```python
response.encoding = 'utf-8'  # 必須設定，確保中文正常
```

### 圖片提取
```python
# 只提取 upload/event/ 路徑的圖片
if 'upload/event/' in src:
    # 處理圖片
```

## 🚨 常見問題速查

| 問題 | 可能原因 | 解決方向 |
|-----|---------|----------|
| 爬取到 0 筆資料 | 網站結構變更 | 檢查 CSS 選擇器 |
| SSL 錯誤 | 憑證問題 | 確認 verify=False |
| 編碼亂碼 | 編碼設定 | 檢查 UTF-8 設定 |
| GitHub Actions 失敗 | 相依套件或權限 | 檢查 requirements.txt 和權限 |

## 🛠️ 快速修改範本

### 添加新欄位
```python
# 在 get_activity_details 中添加
details['new_field'] = extract_new_info(soup)

# 在 generate_readme 中顯示
if activity.get('new_field'):
    readme_content += f"- **新欄位**: {activity['new_field']}\n"
```

### 修改執行時間
```yaml
# .github/workflows/crawler.yml
schedule:
  - cron: '0 1,13 * * *'  # 每日 09:00 和 21:00 台灣時間
```

### 添加錯誤處理
```python
try:
    # 爬取邏輯
except Exception as e:
    logger.warning(f"錯誤描述: {e}")
    # 繼續處理其他項目
```

## 📋 修改檢查清單

- [ ] 保持現有 JSON 結構不變
- [ ] 添加適當的錯誤處理和日誌
- [ ] 測試修改後的功能
- [ ] 更新相關文件
- [ ] 確認 GitHub Actions 可正常執行

## 🔄 測試命令

```bash
# 本地測試
python crawler.py

# 檢查輸出
cat data/latest_activities.json

# 檢查圖片 URL（如果有 curl）
curl -I "圖片URL"
```

---
*此檔案提供 Claude AI 快速了解專案的核心資訊*
