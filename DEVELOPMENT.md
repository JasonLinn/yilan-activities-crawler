# Claude AI 開發指南 - 宜蘭活動爬蟲專案

## 📋 專案概述

本專案是一個自動化的宜蘭縣文化局活動資訊爬蟲系統，目標是定期收集、整理並展示宜蘭縣的各類文化活動資訊。

### 🎯 核心目標
- 自動化爬取宜蘭縣文化局活動資訊
- 提取結構化資料（標題、時間、地點、圖片等）
- 自動生成使用者友善的展示頁面
- 透過 GitHub Actions 實現定期自動執行

## 🏗️ 專案架構

### 核心檔案結構
```
yilan-activities-crawler/
├── crawler.py                 # 主要爬蟲程式
├── requirements.txt           # Python 相依套件
├── README.md                 # 自動生成的專案說明
├── GUIDE.md                  # 使用者操作指南
├── DEVELOPMENT.md            # 本開發指南
├── .github/workflows/
│   └── crawler.yml           # GitHub Actions 工作流程
└── data/                     # 爬取的資料目錄
    ├── latest_activities.json # 最新活動資料
    └── yilan_activities_*.json # 歷史資料
```

### 🔧 核心函式說明

#### `get_activity_details(session, activity_url)`
- **目的**: 獲取單個活動的詳細資訊
- **輸入**: requests Session 物件、活動詳情頁面 URL
- **輸出**: 包含圖片和描述的字典
- **重要**: 此函式負責深度解析活動頁面，提取圖片等詳細資訊

#### `crawl_yilan_activities()`
- **目的**: 主要爬取函式
- **功能**: 爬取活動列表頁面，解析活動基本資訊，呼叫詳情獲取函式
- **輸出**: 活動資料列表

#### `generate_readme()`
- **目的**: 生成 README.md 展示頁面
- **功能**: 將爬取的 JSON 資料轉換為 Markdown 格式

## 🛠️ 開發規範

### 1. 程式碼修改原則

#### ✅ 應該做的事
- **保持向後相容性**: 任何修改都不應破壞現有的資料結構
- **錯誤處理**: 所有網路請求都應包含適當的錯誤處理
- **日誌記錄**: 使用 logger 記錄重要操作和錯誤
- **編碼處理**: 確保正確處理中文編碼 (UTF-8)
- **SSL 處理**: 保持 SSL 憑證驗證忽略的設定（目標網站憑證問題）

#### ❌ 避免的事
- **不要移除現有欄位**: 避免移除 JSON 資料中的現有欄位
- **不要硬編碼**: 避免硬編碼 URL 或選擇器
- **不要忽略錯誤**: 不要讓單個失敗影響整體爬取
- **不要破壞格式**: 保持 JSON 和 Markdown 輸出格式的一致性

### 2. 資料結構規範

#### 活動資料標準格式
```json
{
  "title": "活動標題",
  "category": "活動類型 (展覽/表演/研習/故事/活動)",
  "date": "2025-09-01 (Mon)",
  "price": "票價資訊 (免票入場/線上購票/未知)",
  "location": "活動地點",
  "url": "活動詳情連結",
  "images": [
    {
      "url": "圖片完整 URL",
      "alt": "圖片描述"
    }
  ],
  "description": "活動描述 (可選)",
  "crawl_time": "爬取時間戳記"
}
```

#### 輸出檔案格式
```json
{
  "update_time": "更新時間",
  "total_count": "活動總數",
  "activities": ["活動資料陣列"]
}
```

### 3. 網站結構分析指南

#### 目標網站: https://yilanart.ilccb.gov.tw/index.php?inter=activity

**主要頁面結構**:
- 活動列表頁面: 包含活動連結列表
- 活動詳情頁面: 包含完整活動資訊和圖片

**重要 CSS 選擇器**:
- 內容區域: `div.content`
- 活動連結: 包含 `did=` 參數的 `<a>` 標籤
- 活動圖片: `img[src*="upload/event/"]`

**資料提取模式**:
1. 從列表頁面獲取活動連結
2. 訪問每個活動詳情頁面
3. 提取圖片和詳細描述
4. 解析活動標題中的時間和分類資訊

## 🔄 維護和除錯指南

### 1. 常見問題處理

#### 問題: 爬取到空資料
**診斷步驟**:
1. 檢查目標網站是否可訪問
2. 驗證 CSS 選擇器是否仍然有效
3. 檢查網站結構是否有變更

**解決方案**:
```python
# 在 crawler.py 中添加除錯資訊
logger.info(f"找到 {len(activity_links)} 個活動連結")
if not activity_links:
    logger.warning("未找到活動連結，可能網站結構已變更")
```

#### 問題: SSL 憑證錯誤
**已實現解決方案**:
```python
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

#### 問題: 編碼錯誤
**解決方案**:
```python
response.encoding = 'utf-8'
```

### 2. 效能最佳化

#### 請求頻率控制
```python
import time
time.sleep(0.5)  # 在請求間添加延遲
```

#### 逾時設定
```python
response = session.get(url, timeout=30)
```

## 🚀 擴展功能指南

### 1. 添加新的活動來源

**步驟**:
1. 建立新的爬取函式
2. 統一資料格式
3. 修改主函式整合新來源
4. 更新 README 生成邏輯

**範例架構**:
```python
def crawl_new_source():
    """爬取新的活動來源"""
    # 實作爬取邏輯
    return activities

def main():
    yilan_activities = crawl_yilan_activities()
    new_activities = crawl_new_source()
    all_activities = yilan_activities + new_activities
    # 處理合併和去重
```

### 2. 添加圖片下載功能

**實作建議**:
```python
def download_images(activities):
    """下載活動圖片到本地"""
    for activity in activities:
        for img in activity.get('images', []):
            # 下載圖片邏輯
            pass
```

### 3. 添加資料分析功能

**可能的擴展**:
- 活動趨勢分析
- 地點熱度統計
- 活動類型分佈圖表

## 🧪 測試指南

### 1. 本地測試

**基本測試**:
```bash
python crawler.py
```

**檢查輸出**:
1. 驗證 JSON 檔案格式
2. 檢查 README.md 生成
3. 確認圖片 URL 可訪問

### 2. 單元測試建議

**測試函式**:
```python
def test_activity_parsing():
    """測試活動資料解析"""
    pass

def test_image_extraction():
    """測試圖片提取"""
    pass
```

## 📊 監控和日誌

### 1. 重要日誌點

- 開始爬取: `logger.info("開始爬取: {url}")`
- 成功獲取: `logger.info("成功取得網頁內容")`
- 資料統計: `logger.info("成功爬取 {count} 筆活動資料")`
- 錯誤處理: `logger.error("錯誤資訊")`

### 2. GitHub Actions 監控

**檢查點**:
1. 工作流程執行狀態
2. 爬取資料數量變化
3. 錯誤日誌分析

## 🔐 安全性考量

### 1. 網站禮儀
- 合理的請求間隔
- 適當的 User-Agent
- 遵守 robots.txt

### 2. 資料隱私
- 只爬取公開的活動資訊
- 不收集個人資料
- 遵守資料使用規範

## 📚 相依套件管理

### 核心相依套件
```
requests==2.31.0     # HTTP 請求
beautifulsoup4==4.12.2  # HTML 解析
```

### 升級指南
1. 測試新版本相容性
2. 更新 requirements.txt
3. 驗證 GitHub Actions 執行

## 🚨 緊急處理程序

### 1. 服務中斷
1. 檢查目標網站狀態
2. 查看 GitHub Actions 日誌
3. 必要時暫停自動執行

### 2. 資料異常
1. 備份現有資料
2. 分析問題原因
3. 修復後重新爬取

## 📝 變更記錄規範

### Commit 訊息格式
```
🐛 修復: 描述修復的問題
✨ 功能: 描述新增的功能
📝 文件: 描述文件更新
🔧 維護: 描述維護性變更
```

### 版本標籤
使用語意化版本號：`v1.0.0`

---

## 🤖 Claude AI 特別指示

### 程式碼修改時的檢查清單
- [ ] 保持現有資料結構
- [ ] 添加適當的錯誤處理
- [ ] 更新相關文件
- [ ] 測試修改的功能
- [ ] 確保 GitHub Actions 相容性

### 問題解決流程
1. **理解問題**: 仔細分析使用者的需求
2. **評估影響**: 判斷修改對現有功能的影響
3. **實作解決方案**: 逐步實作並測試
4. **文件更新**: 更新相關指南和說明
5. **驗證結果**: 確保解決方案有效

### 溝通原則
- 清楚說明修改的內容和原因
- 提供測試步驟和驗證方法
- 說明可能的風險和注意事項
- 建議後續的維護方向

---

*本開發指南應隨專案演進持續更新*
*最後更新：2025-09-01*
