# 天堂M 裝備網站爬蟲

這個專案爬取 [天堂M 裝備資訊網站](https://www.gametsg.net/equip.html) 上的裝備資訊。

## 功能

1. **基本爬蟲**: 僅爬取裝備類別 (`lineage_m_scraper.py`)
   - 找到所有裝備種類
   - 儲存成 CSV 檔案

2. **進階爬蟲**: 爬取裝備類別及各類別的裝備資訊 (`advanced_scraper.py`)
   - 找到所有裝備種類
   - 爬取各種類的裝備詳細資訊
   - 儲存成 CSV 和 JSON 格式
   
3. **詳細資訊爬蟲**: 爬取每個裝備的詳細頁面資訊 (`item_detail_fetcher.py`)
   - 讀取所有裝備的JSON資料
   - 抓取每個裝備的詳細頁面
   - 解析完整資訊，包含：
     - 基本訊息 (類型、職業、攻擊力、屬性等)
     - 細節資訊 (損傷、倉庫、交換、安定值等)
     - 製作材料 (包含所需材料、數量和可選材料)
     - 強化訊息 (各等級強化的詳細屬性)
     - 怪物掉落訊息 (掉落此物品的怪物資訊)
   - 儲存為獨立的JSON檔案

3. **詳細物品資訊爬蟲**: 爬取每個裝備的詳細資訊 (`item_detail_scraper.py`)
   - 從裝備類別 JSON 檔案讀取類別資訊
   - 解析每個類別頁面中的 `itemList` div 內的所有物品
   - 擷取物品名稱、圖片、適用職業、等級、屬性等資訊
   - 儲存成 Excel 和 JSON 格式

## 安裝需求

使用以下命令安裝必要套件：

```
pip install -r requirements.txt
```

主要依賴套件：
- requests: 用於發送 HTTP 請求
- beautifulsoup4: 用於解析 HTML
- pandas: 用於數據處理及輸出 CSV

## 使用方法

### 方法 1: 使用選單界面

執行選單界面，可以選擇要進行的爬蟲任務：

```
python run_scraper_menu.py
```

選單選項:
1. 爬取裝備種類 (基本爬蟲)
2. 爬取裝備列表 (進階爬蟲)
3. 爬取裝備詳細資料
4. 執行完整爬蟲流程 (1+2+3)
5. 修復JSON檔案
0. 退出

### 方法 2: 執行整合腳本

直接執行整合腳本，它會依序執行基本爬蟲、進階爬蟲和詳細資訊爬蟲：

```
python run_scraper.py
```

### 方法 3: 單獨執行各爬蟲

執行基本爬蟲 (爬取裝備種類)：

```
python lineage_m_scraper.py
```

執行進階爬蟲 (爬取裝備列表)：

```
python advanced_scraper.py
```

執行詳細資訊爬蟲 (爬取裝備詳細頁面)：

```
python item_detail_fetcher.py
```

修復JSON檔案：

```
python fix_json.py
```

執行詳細物品資訊爬蟲：

```
python item_detail_scraper.py
```

## 輸出資料

本爬蟲系統會產生多種資料輸出：

### 基本爬蟲輸出
- 根目錄: `equipment_categories.csv` (裝備類別基本資訊)

### 進階爬蟲輸出 (scraped_data 資料夾)
- `equipment_categories.csv` / `equipment_categories.json`: 裝備類別資訊
- **excel 資料夾**: 各裝備類別的資料文件，格式為 `items_{類別ID}_{類別名稱}.xlsx`
  - `all_items.xlsx`: 所有裝備資訊合併檔 (Excel格式)
- **json 資料夾**: 各裝備類別的資料文件，格式為 `items_{類別ID}_{類別名稱}.json`
  - `all_items.json`: 所有裝備資訊合併檔 (JSON格式)

### 詳細資訊爬蟲輸出 (scraped_items 資料夾)
- 每個裝備獨立的JSON檔案，命名格式為「物品名稱_物品ID.json」，包含以下資訊:
  - 基本物品資訊 (從列表爬蟲獲取)
  - 基本訊息 (類型、職業、攻擊力、屬性等)
  - 細節資訊 (損傷、倉庫、交換、安定值等)
  - 製作材料 (所需材料名稱、數量、可選材料等)
  - 強化訊息 (各等級強化的詳細屬性)
  - 怪物掉落訊息 (掉落此物品的怪物、體型、等級、弱點、刷新區域等)

詳細物品資訊爬蟲會產生以下文件：
- `scraped_data/json/` 資料夾: 包含所有 JSON 格式的物品資料
- `scraped_data/excel/` 資料夾: 包含所有 Excel 格式的物品資料
- 各裝備類別的資料文件，格式為 `items_{類別ID}_{類別名稱}.xlsx/json`
- `all_items.xlsx` / `all_items.json`: 所有物品詳細資訊合併檔

## 注意事項

- 爬蟲程式已內建休息時間，以避免對網站造成過大負擔
- 請不要頻繁運行爬蟲，以免影響網站正常運行
- 此爬蟲僅供學習和研究用途，請尊重網站的使用條款
