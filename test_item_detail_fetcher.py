"""
測試爬取單一物品詳細資訊的腳本
"""

import sys
import json
from item_detail_fetcher import ItemDetailFetcher

def test_item_detail_fetcher():
    """
    測試爬取單一物品的詳細資訊
    """
    print("===== 測試爬取單一物品詳細資訊 =====")
    
    # 建立測試物品
    test_item = {
        "item_id": "23",
        "item_name": "屠龍劍",
        "item_url": "https://www.gametsg.net/equip/detail.html?id=23",
        "item_image": "https://www.gametsg.net/img/1/1/980f780f66bfc358e1973204f508bb3e.jpg",
        "category_name": "單手劍"
    }
    
    # 創建爬蟲實例
    fetcher = ItemDetailFetcher("scraped_data/json/all_items.json")
    
    # 爬取詳細資訊
    print(f"開始爬取物品 '{test_item['item_name']}' 的詳細資訊...")
    detailed_item = fetcher.fetch_item_details(test_item)
    
    if detailed_item:
        # 顯示結果
        print("\n爬取結果:")
        print(f"- 物品名稱: {detailed_item['item_name']}")
        
        if 'basic_info' in detailed_item:
            print("\n基本訊息:")
            for key, value in detailed_item['basic_info'].items():
                print(f"- {key}: {value}")
        
        if 'detail_info' in detailed_item:
            print("\n細節資訊:")
            for key, value in detailed_item['detail_info'].items():
                print(f"- {key}: {value}")
        
        if 'craft_materials' in detailed_item and detailed_item['craft_materials']:
            print("\n製作材料:")
            for material in detailed_item['craft_materials']:
                print(f"- {material.get('material_name', '')} x {material.get('material_count', '')}")
                # Display alternatives if available
                if 'alternatives' in material and material['alternatives']:
                    print("  可選材料:")
                    for alt in material['alternatives']:
                        print(f"  - {alt.get('alt_name', '')} x {alt.get('alt_count', '')}")
        
        if 'enhance_info' in detailed_item:
            print("\n強化訊息:")
            for enhance in detailed_item['enhance_info'][:3]:  # Show only first 3 for brevity
                print(f"- 等級 {enhance['level']}: {enhance['attributes']}")
            print(f"  ... (共 {len(detailed_item['enhance_info'])} 個強化等級)")
        
        if 'monster_drops' in detailed_item and detailed_item['monster_drops']:
            print("\n怪物掉落訊息:")
            for monster in detailed_item['monster_drops']:
                print(f"- 怪物: {monster.get('monster_name', '')} (等級: {monster.get('monster_level', '')})")
                print(f"  體型: {monster.get('monster_size', '')}")
                print(f"  弱點: {', '.join([w.get('type', '') for w in monster.get('monster_weaknesses', [])])}")
                print(f"  刷新區域: {', '.join(monster.get('monster_areas', []))}")
        
        # 儲存測試結果
        output_path = "test_item_detail.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_item, f, ensure_ascii=False, indent=2)
        print(f"\n結果已儲存至: {output_path}")
    else:
        print("爬取失敗，未能獲取詳細資訊。")

if __name__ == "__main__":
    test_item_detail_fetcher()
