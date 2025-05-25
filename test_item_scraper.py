# 天堂M 物品詳細資訊爬蟲測試腳本

from item_detail_scraper import ItemDetailScraper
from datetime import datetime
import os

def test_item_detail_scraper():
    """
    測試物品詳細資訊爬蟲
    """
    print(f"開始測試物品詳細資訊爬蟲，時間: {datetime.now()}")
    
    # 檢查categories.json檔案是否存在
    categories_json_path = "scraped_data/equipment_categories.json"
    if not os.path.exists(categories_json_path):
        print(f"找不到類別資料檔案: {categories_json_path}")
        print("請先執行基本爬蟲或進階爬蟲生成類別資料!")
        return False
    
    # 建立詳細物品資訊爬蟲實例
    scraper = ItemDetailScraper(categories_json_path)
    
    # 載入類別資料
    categories = scraper.load_categories()
    if not categories:
        print("無法載入類別資料!")
        return False
    
    print(f"成功載入 {len(categories)} 個裝備類別")
    
    # 測試模式：只爬取前3個類別的資料
    test_categories = categories[:3]
    print(f"測試模式：將只爬取前 {len(test_categories)} 個類別的資料")
    
    for category in test_categories:
        print(f"\n測試爬取類別: {category['category_name']} (ID: {category['type_id']})")
        items = scraper.scrape_category_page(category)
        
        if items:
            # 儲存測試資料
            category_filename = f"test_items_{category['type_id']}_{category['category_name']}"
            scraper.save_to_json(items, f"{category_filename}.json")
            scraper.save_to_excel(items, f"{category_filename}.xlsx")
    
    print(f"\n測試完成，時間: {datetime.now()}")
    print("測試結果已儲存在 scraped_data/json 和 scraped_data/excel 資料夾中")
    return True

if __name__ == "__main__":
    test_item_detail_scraper()
