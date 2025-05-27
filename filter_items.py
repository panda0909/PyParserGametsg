import json
import os
import argparse
from collections import Counter

def filter_items(analyze=False, output_path=None):
    """
    Filter items from all_items.json where item_name is empty but item_url is not empty
    
    Args:
        analyze (bool): Whether to analyze the filtered data
        output_path (str): Custom output path for the filtered data
    """
    # Path to the all_items.json file
    input_file = os.path.join('scraped_data', 'json', 'all_items.json')
    
    # Path for the filtered output
    if not output_path:
        output_file = os.path.join('scraped_data', 'json', 'filtered_items.json')
    else:
        output_file = output_path
    
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            all_items = json.load(f)
            
        print(f"Loaded {len(all_items)} items from {input_file}")
        
        # Filter items where item_name is empty but item_url is not empty
        filtered_items = [item for item in all_items if item.get('item_name', '') == '' and item.get('item_url', '') != '']
        
        print(f"Found {len(filtered_items)} items where item_name is empty but item_url is not empty")
        
        # Write the filtered items to a new JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_items, f, ensure_ascii=False, indent=2)
            
        print(f"Filtered items saved to {output_file}")
        
        # Print first few filtered items as a sample
        if filtered_items:
            print("\nSample of filtered items:")
            for i, item in enumerate(filtered_items[:5]):
                print(f"{i+1}. ID: {item.get('item_id', 'N/A')}, URL: {item.get('item_url')}")
                
        # Additional analysis if requested
        if analyze and filtered_items:
            analyze_filtered_data(filtered_items)
            
    except Exception as e:
        print(f"Error: {e}")

def analyze_filtered_data(filtered_items):
    """
    Analyze the filtered data to provide more insights
    
    Args:
        filtered_items (list): List of filtered item dictionaries
    """
    print("\n=== Analysis of Filtered Items ===")
    
    # Count items by category
    categories = Counter([item.get('category_name', 'Unknown') for item in filtered_items])
    print("\nItems by Category:")
    for category, count in categories.most_common():
        print(f"- {category}: {count} items")
    
    # Check if there are item_id patterns
    print("\nItem ID Range:")
    item_ids = [int(item['item_id']) for item in filtered_items if item.get('item_id', '').isdigit()]
    if item_ids:
        print(f"- Min ID: {min(item_ids)}")
        print(f"- Max ID: {max(item_ids)}")
    
    # Check if items have images
    with_images = sum(1 for item in filtered_items if item.get('item_image', '') != '')
    print(f"\n{with_images} out of {len(filtered_items)} items have images ({with_images/len(filtered_items)*100:.1f}%)")
    
    # Check for any patterns in item_stats
    stats_count = Counter()
    for item in filtered_items:
        for stat in item.get('item_stats', []):
            if stat:
                stats_count[stat] += 1
    
    if stats_count:
        print("\nCommon stats/descriptions:")
        for stat, count in stats_count.most_common(5):
            print(f"- \"{stat}\": appears in {count} items")

def main():
    """Parse command line arguments and run the filter"""
    parser = argparse.ArgumentParser(description='Filter and analyze items from all_items.json')
    parser.add_argument('--analyze', action='store_true', help='Analyze the filtered data')
    parser.add_argument('--output', type=str, help='Custom output path for filtered data')
    
    args = parser.parse_args()
    
    filter_items(analyze=args.analyze, output_path=args.output)

if __name__ == "__main__":
    main()
