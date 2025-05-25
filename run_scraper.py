# 天堂M 裝備爬蟲使用指南

# 1. 首先安裝必要的套件:
# pip install -r requirements.txt

import os
import time
from datetime import datetime

print(f"開始執行爬蟲程式，時間: {datetime.now()}\n")

# 2. 基本爬蟲 (只爬取裝備種類):
from lineage_m_scraper import LineageMScraper

print("===== 執行基本爬蟲 =====")
# 建立爬蟲實例
basic_scraper = LineageMScraper()

# 爬取裝備種類
categories = basic_scraper.get_equipment_categories()

# 將結果儲存為CSV
basic_scraper.save_categories_to_csv()

print("\n基本爬蟲完成!\n")
time.sleep(1)

# 3. 進階爬蟲 (爬取裝備種類和各類別的裝備):
from advanced_scraper import LineageMScraper as AdvancedScraper

print("===== 執行進階爬蟲 =====")
# 建立進階爬蟲實例
advanced_scraper = AdvancedScraper()

# 爬取裝備種類和所有裝備
advanced_scraper.get_equipment_categories()
advanced_scraper.scrape_all_categories()

print("\n進階爬蟲完成!\n")
time.sleep(1)

# 4. 詳細物品資訊爬蟲 (爬取物品詳細資訊):
from item_detail_scraper import ItemDetailScraper

print("===== 執行詳細物品資訊爬蟲 =====")
# 檢查categories.json檔案是否存在
categories_json_path = "scraped_data/equipment_categories.json"
if not os.path.exists(categories_json_path):
    print(f"找不到類別資料檔案: {categories_json_path}")
    print("請先執行基本爬蟲或進階爬蟲生成類別資料!")
else:
    # 建立詳細物品資訊爬蟲實例
    detail_scraper = ItemDetailScraper(categories_json_path)
    
    # 爬取所有類別的物品詳細資訊
    detail_scraper.scrape_all_categories()
    
    print("\n詳細物品資訊爬蟲完成!\n")

print(f"所有爬蟲程式執行完成，時間: {datetime.now()}")
print("爬蟲結果儲存於 scraped_data 資料夾中")
