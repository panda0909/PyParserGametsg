import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from datetime import datetime
import logging
import unicodedata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('item_detail_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ItemDetailFetcher:
    def __init__(self, items_json_path):
        """
        Initialize the fetcher with the path to the items JSON file
        """
        self.items_json_path = items_json_path
        self.base_url = "https://www.gametsg.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Create output directory if it doesn't exist
        self.output_dir = "scraped_items"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Keep track of processed items to avoid duplicates
        self.processed_items = set()
    
    def load_items(self):
        """
        Load items from the JSON file
        """
        try:
            with open(self.items_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading items: {str(e)}")
            return []
    
    def clean_text(self, text):
        """
        Clean text by removing extra spaces and newlines
        """
        if text is None:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def sanitize_filename(self, filename):
        """
        Sanitize filename by replacing invalid characters with underscores
        """
        if not filename:
            return "unnamed_item"
            
        # Replace common invalid filename characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\t', '\n', '\r']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Normalize unicode characters
        filename = unicodedata.normalize('NFKD', filename)
            
        # Remove leading/trailing periods and spaces which can cause issues
        filename = filename.strip('. ')
        
        # Ensure the filename is not too long
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename
    
    def extract_basic_info(self, soup, item_data):
        """
        Extract basic information from the item detail page
        """
        basic_info = {}
        
        try:
            # Get item title
            title = soup.select_one('h2.dbTitle')
            if title:
                basic_info['title'] = self.clean_text(title.text)
            
            # Extract from basicList
            basic_list = soup.select('ul.basicList li')
            for li in basic_list:
                label = li.select_one('.ti')
                value = li.select_one('.con')
                
                if label and value:
                    label_text = self.clean_text(label.text)
                    
                    # Handle different value formats
                    if label_text == "職業":
                        classes = []
                        class_spans = value.select('.class')
                        for span in class_spans:
                            class_name = self.clean_text(span.text)
                            class_level = span.get('class')[1] if len(span.get('class', [])) > 1 else ""
                            classes.append({"name": class_name, "level": class_level})
                        basic_info[label_text] = classes
                    elif value.select_one('.conn'):
                        content = value.select_one('.conn')
                        if content:
                            values = [self.clean_text(v) for v in content.text.split("\n") if self.clean_text(v)]
                            if len(values) == 1:
                                basic_info[label_text] = values[0]
                            else:
                                basic_info[label_text] = values
                    else:
                        basic_info[label_text] = self.clean_text(value.text)
            
            return basic_info
        
        except Exception as e:
            logger.error(f"Error extracting basic info for {item_data.get('item_name', '')}: {str(e)}")
            return basic_info
    
    def extract_detail_info(self, soup, item_data):
        """
        Extract detail information from the item detail page
        """
        detail_info = {}
        
        try:
            # Extract from detailTable
            detail_list = soup.select('ul.xjList li')
            for li in detail_list:
                label = li.select_one('.ti')
                value = li.select_one('.con')
                
                if label and value:
                    label_text = self.clean_text(label.text)
                    value_text = self.clean_text(value.text)
                    detail_info[label_text] = value_text
            
            return detail_info
        
        except Exception as e:
            logger.error(f"Error extracting detail info for {item_data.get('item_name', '')}: {str(e)}")
            return detail_info
    
    def extract_enhance_info(self, soup, item_data):
        """
        Extract enhancement information from the item detail page
        """
        enhance_info = []
        
        try:
            # Get enhancement table
            enhance_table = soup.select('div.addList div.tbody ul li')
            for li in enhance_table:
                columns = li.select('.column')
                if len(columns) >= 2:
                    level = self.clean_text(columns[0].text)
                    attributes = self.clean_text(columns[1].text)
                    enhance_info.append({
                        "level": level,
                        "attributes": attributes
                    })
            
            return enhance_info
        
        except Exception as e:
            logger.error(f"Error extracting enhancement info for {item_data.get('item_name', '')}: {str(e)}")
            return enhance_info
    
    def extract_craft_materials(self, soup, item_data):
        """
        Extract manufacturing materials information from the item detail page
        """
        craft_materials = []
        
        try:
            # Check if there's a materials section
            craft_section = soup.select_one('div.craftInfo')
            if not craft_section:
                return craft_materials
            
            # Get materials list
            material_items = craft_section.select('ul.craftList > li')
            for item in material_items:
                material = {}
                
                # Get material link and basic info
                material_link = item.select_one('a')
                if material_link:
                    material['material_url'] = self.base_url + material_link.get('href', '')
                    material['material_id'] = material_link.get('href', '').split('id=')[-1] if 'id=' in material_link.get('href', '') else ''
                    material['material_name'] = self.clean_text(material_link.get('title', ''))
                    
                    # Get material icon
                    material_icon = material_link.select_one('img.itemIcon')
                    if material_icon:
                        material['material_image'] = self.base_url + material_icon.get('src', '')
                    
                    # Get material grade and count
                    name_span = material_link.select_one('span.itemname')
                    if name_span:
                        material['material_grade'] = name_span.get('class', [])[1] if len(name_span.get('class', [])) > 1 else ''
                        
                        # Get count
                        count_span = name_span.select_one('span.count')
                        if count_span:
                            material['material_count'] = self.clean_text(count_span.text)
                
                # Check if there are alternatives
                alternatives = []
                alt_list = item.select('ul.craftList.childList > li.subst')
                for alt in alt_list:
                    alternative = {}
                    
                    alt_link = alt.select_one('a')
                    if alt_link:
                        alternative['alt_url'] = self.base_url + alt_link.get('href', '')
                        alternative['alt_id'] = alt_link.get('href', '').split('id=')[-1] if 'id=' in alt_link.get('href', '') else ''
                        
                        # Get alternative name, grade and count
                        alt_name_span = alt_link.select_one('span.itemname')
                        if alt_name_span:
                            alternative['alt_name'] = self.clean_text(alt_name_span.text.split('x')[0])
                            alternative['alt_grade'] = alt_name_span.get('class', [])[1] if len(alt_name_span.get('class', [])) > 1 else ''
                            
                            # Get count
                            alt_count_span = alt_name_span.select_one('span.count')
                            if alt_count_span:
                                alternative['alt_count'] = self.clean_text(alt_count_span.text)
                    
                    if alternative:
                        alternatives.append(alternative)
                
                if alternatives:
                    material['alternatives'] = alternatives
                
                if material:
                    craft_materials.append(material)
            
            return craft_materials
        
        except Exception as e:
            logger.error(f"Error extracting craft materials for {item_data.get('item_name', '')}: {str(e)}")
            return craft_materials
    
    def extract_monster_drops(self, soup, item_data):
        """
        Extract monster drop information from the item detail page
        """
        monster_drops = []
        
        try:
            # Check if there's a monster drops section
            monster_section = soup.find('h5', class_='infoTit', string='怪物掉落訊息')
            if not monster_section:
                return monster_drops
            
            # Get monster list
            monster_table = monster_section.find_next('div', class_='tbody')
            if not monster_table:
                return monster_drops
                
            monster_rows = monster_table.select('ul > li')
            for row in monster_rows:
                monster = {}
                columns = row.select('.column')
                
                # Ensure we have enough columns
                if len(columns) < 5:
                    continue
                
                # Get monster name and URL
                monster_link = columns[0].select_one('a')
                if monster_link:
                    monster['monster_name'] = self.clean_text(monster_link.text)
                    monster['monster_url'] = self.base_url + monster_link.get('href', '')
                    monster['monster_id'] = monster_link.get('href', '').split('id=')[-1] if 'id=' in monster_link.get('href', '') else ''
                    monster['monster_type'] = monster_link.select_one('span').get('class', [])[-1] if monster_link.select_one('span') else ''
                
                # Get monster size
                size_span = columns[1].select_one('.monSize')
                if size_span:
                    monster['monster_size'] = self.clean_text(size_span.text)
                    monster['monster_size_class'] = size_span.get('class', [])[-1] if len(size_span.get('class', [])) > 1 else ''
                
                # Get monster level
                monster['monster_level'] = self.clean_text(columns[2].text)
                
                # Get monster weaknesses
                weaknesses = []
                weakness_spans = columns[3].select('.point')
                for span in weakness_spans:
                    weakness = {
                        'type': self.clean_text(span.text),
                        'class': span.get('class', [])[-1] if len(span.get('class', [])) > 1 else ''
                    }
                    weaknesses.append(weakness)
                
                if weaknesses:
                    monster['monster_weaknesses'] = weaknesses
                
                # Get spawn areas
                monster['monster_areas'] = [self.clean_text(area) for area in columns[4].text.split('\n') if self.clean_text(area)]
                
                if monster:
                    monster_drops.append(monster)
                    
            return monster_drops
            
        except Exception as e:
            logger.error(f"Error extracting monster drop info for {item_data.get('item_name', '')}: {str(e)}")
            return monster_drops
    
    def fetch_item_details(self, item):
        """
        Fetch detailed information for a single item
        """
        item_name = item.get('item_name', '')
        item_url = item.get('item_url', '')
        
        if not item_url or not item_name:
            logger.warning(f"Skipping item with no name or URL: {item}")
            return None
        
        # Check if we've already processed this item
        if item_url in self.processed_items:
            logger.info(f"Skipping already processed item: {item_name}")
            return None
        
        logger.info(f"Fetching details for item: {item_name} (URL: {item_url})")
        
        try:
            response = requests.get(item_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Combine original item data with detailed information
            detailed_item = item.copy()
            
            # Extract information sections
            basic_info = self.extract_basic_info(soup, item)
            detail_info = self.extract_detail_info(soup, item)
            enhance_info = self.extract_enhance_info(soup, item)
            craft_materials = self.extract_craft_materials(soup, item)
            monster_drops = self.extract_monster_drops(soup, item)
            
            detailed_item['basic_info'] = basic_info
            detailed_item['detail_info'] = detail_info
            detailed_item['enhance_info'] = enhance_info
            detailed_item['craft_materials'] = craft_materials
            detailed_item['monster_drops'] = monster_drops
            
            # Mark as processed
            self.processed_items.add(item_url)
            
            return detailed_item
        
        except Exception as e:
            logger.error(f"Error fetching details for {item_name}: {str(e)}")
            return None
    
    def save_item_to_json(self, item_data):
        """
        Save a single item's data to a JSON file
        """
        try:
            item_name = item_data.get('item_name', 'unnamed_item')
            safe_filename = self.sanitize_filename(item_name)
            
            # Add an ID to filename to ensure uniqueness
            item_id = item_data.get('item_id', '')
            if item_id:
                filename = f"{safe_filename}_{item_id}.json"
            else:
                filename = f"{safe_filename}.json"
                
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(item_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved item data to {filepath}")
            
            return filepath
        except Exception as e:
            logger.error(f"Error saving item data: {str(e)}")
            return None
    
    def process_all_items(self, max_items=None, delay=1):
        """
        Process all items from the JSON file
        
        Args:
            max_items: Maximum number of items to process (None for all)
            delay: Delay between requests in seconds
        """
        items = self.load_items()
        if not items:
            logger.error("No items found to process")
            return
        
        logger.info(f"Loaded {len(items)} items from {self.items_json_path}")
        
        # Process items with URLs
        items_with_url = [item for item in items if item.get('item_url')]
        logger.info(f"Found {len(items_with_url)} items with URLs to process")
        
        if max_items:
            items_with_url = items_with_url[:max_items]
            logger.info(f"Limiting processing to {max_items} items")
        
        processed_count = 0
        success_count = 0
        
        for item in items_with_url:
            # Fetch detailed information
            detailed_item = self.fetch_item_details(item)
            
            if detailed_item:
                # Save to JSON file
                if self.save_item_to_json(detailed_item):
                    success_count += 1
            
            processed_count += 1
            
            # Print progress
            if processed_count % 10 == 0:
                logger.info(f"Progress: {processed_count}/{len(items_with_url)} items processed")
            
            # Be nice to the server
            time.sleep(delay)
        
        logger.info(f"Completed processing. Total items processed: {processed_count}")
        logger.info(f"Successfully saved details for {success_count} items")
        logger.info(f"Item details saved to directory: {os.path.abspath(self.output_dir)}")

# Entry point
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting item detail fetcher at {start_time}")
    
    # Path to items JSON file
    items_json_path = "scraped_data/json/all_items.json"
    
    # Create and run fetcher
    fetcher = ItemDetailFetcher(items_json_path)
    
    # Process items (optionally limit the number for testing)
    # Set max_items=None to process all items
    fetcher.process_all_items(max_items=None, delay=1)
    
    end_time = datetime.now()
    logger.info(f"Fetching completed at {end_time}")
    logger.info(f"Total time: {end_time - start_time}")
