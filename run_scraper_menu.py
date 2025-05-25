# 天堂M 裝備爬蟲使用指南

import sys
import os
import time
from datetime import datetime

def print_header(text):
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def main():
    # 顯示功能選單
    print_header("天堂M 裝備爬蟲系統")
    print("請選擇要執行的功能：")
    print("1. 爬取裝備種類 (基本爬蟲)")
    print("2. 爬取裝備列表 (進階爬蟲)")
    print("3. 爬取裝備詳細資料")
    print("4. 執行完整爬蟲流程 (1+2+3)")
    print("5. 修復JSON檔案")
    print("0. 退出")
    
    choice = input("\n請輸入選擇 (0-5): ")
    
    if choice == "1":
        run_basic_scraper()
    elif choice == "2":
        run_advanced_scraper()
    elif choice == "3":
        run_item_detail_fetcher()
    elif choice == "4":
        run_complete_workflow()
    elif choice == "5":
        fix_json_file()
    elif choice == "0":
        print("\n感謝使用，程式結束。")
        sys.exit(0)
    else:
        print("\n選擇無效，請重新選擇。")
        main()

def run_basic_scraper():
    print_header("執行基本爬蟲 (爬取裝備種類)")
    
    from lineage_m_scraper import LineageMScraper
    
    # 建立爬蟲實例
    scraper = LineageMScraper()
    
    # 爬取裝備種類
    categories = scraper.get_equipment_categories()
    
    # 將結果儲存為CSV
    scraper.save_categories_to_csv()
    
    print("\n基本爬蟲完成!")
    print(f"已爬取 {len(categories)} 個裝備種類")
    print("檔案儲存於: equipment_categories.csv")
    
    input("\n按 Enter 返回主選單...")
    main()

def run_advanced_scraper():
    print_header("執行進階爬蟲 (爬取裝備列表)")
    
    from advanced_scraper import LineageMScraper as AdvancedScraper
    
    # 檢查基本爬蟲結果是否存在
    if not os.path.exists("scraped_data/equipment_categories.json"):
        print("找不到裝備種類資料，請先執行基本爬蟲！")
        input("\n按 Enter 返回主選單...")
        main()
        return
    
    # 建立進階爬蟲實例
    scraper = AdvancedScraper()
    
    # 爬取裝備種類和所有裝備
    scraper.get_equipment_categories()
    scraper.scrape_all_categories()
    
    print("\n進階爬蟲完成!")
    print("爬蟲結果儲存於 scraped_data 資料夾中")
    
    input("\n按 Enter 返回主選單...")
    main()

def run_item_detail_fetcher():
    print_header("執行裝備詳細資料爬蟲")
    
    from item_detail_fetcher import ItemDetailFetcher
    
    # 檢查進階爬蟲結果是否存在
    all_items_path = "scraped_data/json/all_items.json"
    if not os.path.exists(all_items_path):
        print(f"找不到裝備列表資料: {all_items_path}")
        print("請先執行進階爬蟲！")
        input("\n按 Enter 返回主選單...")
        main()
        return
        
    # 創建並運行詳細資料爬蟲
    items_json_path = "scraped_data/json/all_items.json"
    
    # 詢問使用者是否限制爬蟲數量
    limit_choice = input("是否限制爬取的物品數量？(y/n): ")
    
    max_items = None
    if limit_choice.lower() == 'y':
        try:
            max_items = int(input("請輸入要爬取的物品數量: "))
        except ValueError:
            print("輸入無效，將爬取所有物品")
    
    # 詢問使用者設定延遲時間
    delay = 1  # 預設延遲1秒
    try:
        delay_input = input("請輸入每次爬蟲的延遲秒數 (預設1秒): ")
        if delay_input:
            delay = float(delay_input)
    except ValueError:
        print("輸入無效，將使用預設延遲1秒")
    
    # 建立詳細資料爬蟲實例
    fetcher = ItemDetailFetcher(items_json_path)
    
    # 開始爬取
    start_time = datetime.now()
    print(f"開始爬取裝備詳細資料，時間: {start_time}")
    
    fetcher.process_all_items(max_items=max_items, delay=delay)
    
    end_time = datetime.now()
    print(f"爬蟲完成，時間: {end_time}")
    print(f"總花費時間: {end_time - start_time}")
    print("爬蟲結果儲存於 scraped_items 資料夾中")
    
    input("\n按 Enter 返回主選單...")
    main()

def fix_json_file():
    print_header("修復 JSON 檔案")
    
    from fix_json import fix_json_file
    
    # 檢查JSON檔案是否存在
    json_file_path = "scraped_data/json/all_items.json"
    if not os.path.exists(json_file_path):
        print("找不到要修復的JSON檔案: " + json_file_path)
        input("\n按 Enter 返回主選單...")
        main()
        return
        
    print(f"正在修復JSON檔案: {json_file_path}")
    result = fix_json_file(json_file_path)
    
    if result:
        print("JSON檔案修復成功!")
    else:
        print("JSON檔案修復失敗，請查看錯誤訊息")
    
    input("\n按 Enter 返回主選單...")
    main()

def run_complete_workflow():
    print_header("執行完整爬蟲流程")
    
    print("步驟 1/4: 修復JSON檔案...")
    if os.path.exists("scraped_data/json/all_items.json"):
        from fix_json import fix_json_file
        fix_json_file("scraped_data/json/all_items.json")
        print("JSON檔案修復完成")
    
    # 執行基本爬蟲
    print("\n步驟 2/4: 爬取裝備種類...")
    from lineage_m_scraper import LineageMScraper
    basic_scraper = LineageMScraper()
    categories = basic_scraper.get_equipment_categories()
    basic_scraper.save_categories_to_csv()
    print("裝備種類爬取完成")
    
    # 執行進階爬蟲
    print("\n步驟 3/4: 爬取裝備列表...")
    from advanced_scraper import LineageMScraper as AdvancedScraper
    advanced_scraper = AdvancedScraper()
    advanced_scraper.get_equipment_categories()
    advanced_scraper.scrape_all_categories()
    print("裝備列表爬取完成")
    
    # 執行詳細資料爬蟲
    print("\n步驟 4/4: 爬取裝備詳細資料...")
    from item_detail_fetcher import ItemDetailFetcher
    
    # 詢問使用者設定選項
    try:
        max_items = int(input("請輸入要爬取的最大物品數量 (輸入0表示全部爬取): "))
        if max_items <= 0:
            max_items = None
    except ValueError:
        print("輸入無效，將爬取所有物品")
        max_items = None
    
    try:
        delay = float(input("請輸入每次爬蟲的延遲秒數 (預設1秒): ") or "1")
    except ValueError:
        print("輸入無效，將使用預設延遲1秒")
        delay = 1
    
    # 執行詳細資料爬蟲
    items_json_path = "scraped_data/json/all_items.json"
    fetcher = ItemDetailFetcher(items_json_path)
    fetcher.process_all_items(max_items=max_items, delay=delay)
    
    print("\n完整爬蟲流程已完成!")
    
    input("\n按 Enter 返回主選單...")
    main()

if __name__ == "__main__":
    main()
