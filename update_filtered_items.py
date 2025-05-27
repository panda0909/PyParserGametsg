import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='update_filtered_items.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger('').addHandler(console)

def extract_item_name(soup):
    """Extract item name from the page"""
    try:
        name_div = soup.select_one('div.name')
        if name_div and name_div.select_one('span'):
            return name_div.select_one('span').text.strip()
        elif soup.select_one('h2.dbTitle'):
            # Fallback to the page title if name div is not found
            return soup.select_one('h2.dbTitle').text.strip()
        return ""
    except Exception as e:
        logging.error(f"Error extracting item name: {e}")
        return ""

def extract_monster_drops(soup):
    """Extract monster drop information from the page"""
    monster_drops = []
    
    try:
        monster_list = soup.select_one('div.listTable.monsterList1')
        if not monster_list:
            return monster_drops
            
        monster_rows = monster_list.select('div.tbody ul li')
        
        for row in monster_rows:
            columns = row.select('div.column')
            if len(columns) < 5:
                continue
                
            # Extract monster name and URL
            monster_link = columns[0].select_one('a')
            if not monster_link:
                continue
                
            monster_name = monster_link.text.strip()
            monster_url = f"https://www.gametsg.net{monster_link['href']}"
            monster_id = re.search(r'id=(\d+)', monster_url).group(1) if re.search(r'id=(\d+)', monster_url) else ""
            
            # Extract monster type class
            monster_type_span = columns[0].select_one('span')
            monster_type = monster_type_span['class'][0] if monster_type_span and 'class' in monster_type_span.attrs else "monType01"
            
            # Extract monster size
            monster_size_span = columns[1].select_one('span.monSize')
            monster_size = monster_size_span.text.strip() if monster_size_span else "小型"
            monster_size_class = monster_size_span['class'][1] if monster_size_span and len(monster_size_span['class']) > 1 else "size100"
            
            # Extract monster level
            monster_level = columns[2].text.strip()
            
            # Extract weaknesses
            weaknesses = []
            weak_points = columns[3].select('span.point')
            for weak_point in weak_points:
                weakness_type = weak_point.text.strip()
                weakness_class = weak_point['class'][1] if len(weak_point['class']) > 1 else ""
                weaknesses.append({
                    "type": weakness_type,
                    "class": weakness_class
                })
            
            # Extract monster areas
            monster_areas = [area.strip() for area in columns[4].text.strip().split('<br>') if area.strip()]
            
            monster_drop = {
                "monster_name": monster_name,
                "monster_url": monster_url,
                "monster_id": monster_id,
                "monster_type": monster_type,
                "monster_size": monster_size,
                "monster_size_class": monster_size_class,
                "monster_level": monster_level,
                "monster_weaknesses": weaknesses,
                "monster_areas": monster_areas
            }
            
            monster_drops.append(monster_drop)
            
    except Exception as e:
        logging.error(f"Error extracting monster drops: {e}")
    
    return monster_drops

def fetch_and_update_items(input_file, output_file, start_index=0, max_items=None):
    """
    Fetch web pages and update item information
    
    Args:
        input_file (str): Path to the filtered items JSON file
        output_file (str): Path to save the updated items
        start_index (int): Index to start processing from (for resuming)
        max_items (int): Maximum number of items to process (None for all)
    """
    try:
        # Load filtered items
        with open(input_file, 'r', encoding='utf-8') as f:
            filtered_items = json.load(f)
        
        total_items = len(filtered_items)
        logging.info(f"Loaded {total_items} items from {input_file}")
        
        # Determine how many items to process
        items_to_process = filtered_items[start_index:]
        if max_items is not None:
            items_to_process = items_to_process[:max_items]
        
        logging.info(f"Processing {len(items_to_process)} items starting from index {start_index}")
        
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Process each item
        for i, item in enumerate(items_to_process):
            current_index = start_index + i
            item_url = item.get('item_url', '')
            if not item_url:
                logging.warning(f"Item at index {current_index} has no URL, skipping")
                continue
            
            logging.info(f"Processing item {current_index+1}/{total_items}: {item_url}")
            
            try:
                # Fetch the web page
                response = session.get(item_url, headers=headers)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract item name
                # item_name = extract_item_name(soup)
                # if item_name:
                #     filtered_items[current_index]['item_name'] = item_name
                #     logging.info(f"Updated item name: {item_name}")
                
                # Extract monster drops
                monster_drops = extract_monster_drops(soup)
                if monster_drops:
                    filtered_items[current_index]['monster_drops'] = monster_drops
                    logging.info(f"Added {len(monster_drops)} monster drops")
                
                # Save progress every 10 items
                if (i + 1) % 10 == 0:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(filtered_items, f, ensure_ascii=False, indent=2)
                    logging.info(f"Progress saved after processing {i+1} items")
                
                # Be nice to the server
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error processing item {current_index}: {e}")
                # Continue with the next item even if this one fails
        
        # Save the final results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_items, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Processing complete. Updated data saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Error in fetch_and_update_items: {e}")

def main():
    input_file = os.path.join('scraped_data', 'json', 'nonempty_name_items.json')
    output_file = os.path.join('scraped_data', 'json', 'updated_nonempty_name_items.json')
    
    # Check if arguments are provided
    import argparse
    parser = argparse.ArgumentParser(description='Update filtered items with web data')
    parser.add_argument('--start', type=int, default=0, help='Index to start processing from')
    parser.add_argument('--max', type=int, help='Maximum number of items to process')
    args = parser.parse_args()
    
    fetch_and_update_items(input_file, output_file, args.start, args.max)

if __name__ == "__main__":
    main()
