# 宜蘭縣活動爬蟲操作指南

## 📖 專案簡介

本專案是一個自動化的宜蘭縣文化局活動資訊爬蟲系統，能夠定期爬取並整理宜蘭縣的各類文化活動資訊，包括展覽、表演、研習、故事活動等。

## ✨ 功能特色

- 🤖 **自動化爬取**：使用 GitHub Actions 每日自動執行 2 次
- 📊 **資料整理**：自動分類活動類型、提取時間地點資訊
- 📝 **README 生成**：自動更新專案首頁顯示最新活動
- 🔄 **版本控制**：所有歷史資料都保存在 Git 中
- 💾 **多格式輸出**：JSON 格式便於程式處理

## 🚀 快速開始

### 本地執行

1. **複製專案**：
   ```bash
   git clone https://github.com/JasonLinn/yilan-activities-crawler.git
   cd yilan-activities-crawler
   ```

2. **安裝相依套件**：
   ```bash
   pip install -r requirements.txt
   ```

3. **執行爬蟲**：
   ```bash
   python crawler.py
   ```

### GitHub Actions 自動化設定

#### 步驟 1：推送程式碼到 GitHub

```bash
git add .
git commit -m "初始化宜蘭活動爬蟲專案"
git push origin main
```

#### 步驟 2：啟用 GitHub Actions

1. 進入你的 GitHub 專案頁面
2. 點擊 `Actions` 標籤頁
3. 如果看到工作流程，點擊 `Enable workflow` 啟用

#### 步驟 3：設定權限（如果需要）

1. 進入專案設定：`Settings` > `Actions` > `General`
2. 在 `Workflow permissions` 部分選擇 `Read and write permissions`
3. 勾選 `Allow GitHub Actions to create and approve pull requests`

## ⏰ 執行時程

GitHub Actions 會在以下時間自動執行：

- **每日 09:00** (台灣時間)
- **每日 21:00** (台灣時間)

你也可以手動觸發：

1. 進入 GitHub 專案的 `Actions` 頁面
2. 選擇 `宜蘭活動爬蟲` 工作流程
3. 點擊 `Run workflow` 按鈕

## 📂 檔案結構

```
yilan-activities-crawler/
├── crawler.py                 # 主要爬蟲程式
├── requirements.txt           # Python 相依套件
├── README.md                 # 專案說明（自動生成）
├── GUIDE.md                  # 操作指南（本檔案）
├── .github/
│   └── workflows/
│       └── crawler.yml       # GitHub Actions 設定
└── data/                     # 爬取的資料（自動建立）
    ├── latest_activities.json # 最新活動資料
    └── yilan_activities_*.json # 歷史資料
```

## 🔧 自訂設定

### 修改執行時間

編輯 `.github/workflows/crawler.yml` 檔案的 `cron` 設定：

```yaml
schedule:
  # 每天 UTC 01:00 和 13:00 執行 (台灣時間 09:00 和 21:00)
  - cron: '0 1,13 * * *'
```

### 修改爬取邏輯

主要的爬取邏輯在 `crawler.py` 中：

- `crawl_yilan_activities()` 函式：負責爬取活動資料
- `generate_readme()` 函式：負責生成 README.md

## 📊 資料格式

### JSON 資料結構

```json
{
  "update_time": "2025-09-01 13:14:24",
  "total_count": 12,
  "activities": [
    {
      "title": "活動標題",
      "category": "活動類型",
      "date": "2025-09-01 (Mon)",
      "price": "免票入場",
      "location": "活動地點",
      "url": "活動詳情連結",
      "crawl_time": "2025-09-01 13:14:24"
    }
  ]
}
```

### 活動類型

- **展覽**：藝術展、攝影展等
- **表演**：音樂會、戲劇表演等  
- **研習**：工作坊、研習課程等
- **故事**：故事時間、說故事活動等
- **活動**：其他類型活動

## 🛠️ 疑難排解

### 常見問題

1. **GitHub Actions 執行失敗**
   - 檢查 Actions 頁面的錯誤日誌
   - 確認權限設定正確
   - 檢查 requirements.txt 是否正確

2. **爬取到的資料為空**
   - 檢查目標網站是否變更結構
   - 查看執行日誌中的錯誤訊息

3. **SSL 憑證錯誤**
   - 程式已處理此問題，會自動忽略憑證驗證

### 手動除錯

如果需要除錯，可以在本地執行並查看詳細日誌：

```bash
python crawler.py
```

## 📈 監控與維護

### 檢查執行狀態

1. **GitHub Actions 頁面**：查看工作流程執行歷史
2. **專案首頁**：查看最後更新時間
3. **資料檔案**：檢查 `data/latest_activities.json`

### 定期維護

- 每週檢查 GitHub Actions 執行狀態
- 每月檢查目標網站是否有結構變更
- 需要時更新相依套件版本

## 📚 進階功能

### 添加新的活動來源

如需要爬取其他活動網站，可以：

1. 在 `crawler.py` 中添加新的爬取函式
2. 修改主函式呼叫新的爬取函式
3. 更新資料合併邏輯

### 資料分析

爬取的 JSON 資料可以用於：

- 活動趨勢分析
- 地點熱度統計
- 活動類型分佈
- 價格分析

### 通知功能

可以添加：

- Email 通知
- Slack 通知
- LINE Notify
- Discord Webhook

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個專案！

1. Fork 這個專案
2. 建立你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 📄 授權條款

此專案使用 MIT 授權條款 - 詳見 LICENSE 檔案

## 📞 聯絡資訊

如有問題或建議，請透過 GitHub Issues 聯絡。

---

*最後更新：2025-09-01*
