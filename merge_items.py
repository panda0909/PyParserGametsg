import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('merge_items.log'),
        logging.StreamHandler()
    ]
)

def merge_json_files(filtered_file, nonempty_file, output_file):
    """
    Merge two JSON files into one
    
    Args:
        filtered_file (str): Path to updated_filtered_items.json
        nonempty_file (str): Path to updated_nonempty_name_items.json
        output_file (str): Path to save the merged items
    """
    try:
        # Read the filtered items file
        logging.info(f"Reading data from {filtered_file}")
        with open(filtered_file, 'r', encoding='utf-8') as f:
            filtered_items = json.load(f)
        
        logging.info(f"Loaded {len(filtered_items)} items from {filtered_file}")
        
        # Read the nonempty items file
        logging.info(f"Reading data from {nonempty_file}")
        with open(nonempty_file, 'r', encoding='utf-8') as f:
            nonempty_items = json.load(f)
        
        logging.info(f"Loaded {len(nonempty_items)} items from {nonempty_file}")
        
        # Create a dictionary of filtered items using item_id as key for fast lookup
        filtered_dict = {}
        for item in filtered_items:
            if 'item_id' in item and item['item_id']:
                filtered_dict[item['item_id']] = item
        
        logging.info(f"Created lookup dictionary with {len(filtered_dict)} valid filtered items")
        
        # Create a dictionary of the merged items using item_id as key
        # Start with all nonempty items
        merged_dict = {}
        for item in nonempty_items:
            if 'item_id' in item and item['item_id']:
                merged_dict[item['item_id']] = item
        
        logging.info(f"Added {len(merged_dict)} items from nonempty_items to merged dictionary")
        
        # Update with filtered items that aren't already in merged_dict
        filtered_new_count = 0
        for item_id, item in filtered_dict.items():
            if item_id not in merged_dict:
                merged_dict[item_id] = item
                filtered_new_count += 1
        
        logging.info(f"Added {filtered_new_count} unique items from filtered_items to merged dictionary")
        
        # Convert merged dictionary back to list
        merged_items = list(merged_dict.values())
        
        # Sort by item_id (numeric) for consistent output
        def get_item_id(item):
            try:
                return int(item.get('item_id', '0'))
            except:
                return 0
        
        merged_items.sort(key=get_item_id)
        
        logging.info(f"Final merged list contains {len(merged_items)} items")
        
        # Write the merged items to a new JSON file
        logging.info(f"Saving merged data to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_items, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Successfully saved {len(merged_items)} items to {output_file}")
        
        # Print some statistics about the merged data
        categories = {}
        name_count = 0
        url_count = 0
        monster_drops_count = 0
        
        for item in merged_items:
            # Count by category
            category = item.get('category_name', 'Unknown')
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
            
            # Count items with name and url
            if item.get('item_name', ''):
                name_count += 1
            if item.get('item_url', ''):
                url_count += 1
            if item.get('monster_drops', []):
                monster_drops_count += 1
        
        logging.info(f"Items with names: {name_count}")
        logging.info(f"Items with URLs: {url_count}")
        logging.info(f"Items with monster drops: {monster_drops_count}")
        
        logging.info("Top 10 categories in merged items:")
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories[:10]:
            logging.info(f"  {category}: {count} items")
        
    except Exception as e:
        logging.error(f"Error in merge_json_files: {e}")

def main():
    # Define input and output file paths
    filtered_file = os.path.join('scraped_data', 'json', 'updated_filtered_items.json')
    nonempty_file = os.path.join('scraped_data', 'json', 'updated_nonempty_name_items.json')
    output_file = os.path.join('scraped_data', 'json', 'merge_items.json')
    
    # Merge items
    merge_json_files(filtered_file, nonempty_file, output_file)

if __name__ == "__main__":
    main()
