import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('filter_nonempty_names.log'),
        logging.StreamHandler()
    ]
)

def filter_nonempty_names(input_file, output_file):
    """
    Filter items from all_items.json where item_name is not empty
    
    Args:
        input_file (str): Path to the all_items.json file
        output_file (str): Path to save the filtered items
    """
    try:
        # Read the JSON file
        logging.info(f"Reading data from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            all_items = json.load(f)
            
        total_items = len(all_items)
        logging.info(f"Loaded {total_items} items from {input_file}")
        
        # Filter items where item_name is not empty
        filtered_items = [item for item in all_items if item.get('item_name', '') != '']
        
        filtered_count = len(filtered_items)
        logging.info(f"Found {filtered_count} items where item_name is not empty")
        logging.info(f"Filtered out {total_items - filtered_count} items with empty names")
        
        # Write the filtered items to a new JSON file
        logging.info(f"Saving filtered data to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_items, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Successfully saved {filtered_count} items to {output_file}")
        
        # Print some statistics about the filtered data
        if filtered_items:
            # Count by category
            categories = {}
            for item in filtered_items:
                category = item.get('category_name', 'Unknown')
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
            
            logging.info("Category distribution in filtered items:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                logging.info(f"  {category}: {count} items")
            
    except Exception as e:
        logging.error(f"Error in filter_nonempty_names: {e}")

def main():
    # Define input and output file paths
    input_file = os.path.join('scraped_data', 'json', 'all_items.json')
    output_file = os.path.join('scraped_data', 'json', 'nonempty_name_items.json')
    
    # Filter items
    filter_nonempty_names(input_file, output_file)

if __name__ == "__main__":
    main()
