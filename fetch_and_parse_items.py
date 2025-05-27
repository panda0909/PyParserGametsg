import requests
from bs4 import BeautifulSoup
import json
import os
import time
import logging
import re
from collections import defaultdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_and_parse_items.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ItemFetcher:
    def __init__(self):
        """
        Initialize the fetcher with configurations
        """
        self.merge_items_path = os.path.join("scraped_data", "json", "merge_items.json")
        self.output_path = "final.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.processed_count = 0
        self.final_data = []
        
    def load_merge_items(self):
        """
        Load the merge_items.json file
        """
        try:
            logger.info(f"Loading merge_items.json from {self.merge_items_path}")
            with open(self.merge_items_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {len(data)} items from merge_items.json")
            return data
        except Exception as e:
            logger.error(f"Error loading merge_items.json: {e}")
            return []
    
    def fetch_item_html(self, item):
        """
        Fetch the HTML content for an item URL
        """
        item_url = item.get('item_url')
        item_name = item.get('item_name', 'Unknown')
        
        if not item_url:
            logger.warning(f"No URL found for item: {item_name}")
            return None
        
        try:
            logger.info(f"Fetching HTML for item: {item_name} from {item_url}")
            response = requests.get(item_url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching HTML for {item_name}: {e}")
            return None
    
    def parse_item_html(self, html_content, item):
        """
        Parse the HTML content to extract item details
        """
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Create a copy of the original item to add detailed information
        detailed_item = item.copy()
        
        # Extract basic information
        basic_info = self.extract_basic_info(soup)
        detail_info = self.extract_detail_info(soup)
        enhance_info = self.extract_enhance_info(soup)
        monster_drops = self.extract_monster_drops(soup)
        
        # Add extracted information to the detailed_item
        if basic_info:
            detailed_item.update(basic_info)
        
        if 'item_stats' not in detailed_item and 'item_stats' in basic_info:
            detailed_item['item_stats'] = basic_info.get('item_stats', [])
            
        if 'item_stats2' not in detailed_item and 'item_stats2' in basic_info:
            detailed_item['item_stats2'] = basic_info.get('item_stats2', [])
            
        if detail_info:
            for key, value in detail_info.items():
                if value and key not in detailed_item:
                    detailed_item[key] = value
                    
        if enhance_info:
            detailed_item['enhance_info'] = enhance_info
            
        if monster_drops:
            detailed_item['monster_drops'] = monster_drops
            
        return detailed_item
        
    def extract_basic_info(self, soup):
        """
        Extract basic information about the item
        """
        basic_info = {}
        
        # Extract item grade (class name in <span> element)
        try:
            grade_span = soup.select_one('.itemTit .name span')
            if grade_span and 'class' in grade_span.attrs:
                basic_info['item_grade'] = grade_span['class'][0]
        except Exception as e:
            logger.warning(f"Error extracting item grade: {e}")
        
        # Extract item classes (职业)
        try:
            class_elements = soup.select('.basicList .ti:contains("職業") + .con .class')
            if class_elements:
                item_classes = []
                for class_elem in class_elements:
                    class_name = class_elem.text.strip()
                    class_level = class_elem.get('class', [''])[0] if 'class' in class_elem.attrs else ''
                    item_classes.append({
                        'name': class_name,
                        'level': class_level
                    })
                basic_info['item_classes'] = item_classes
                
                # Build data_zhiye string from class levels
                if item_classes:
                    class_levels = [c['level'].replace('level', '') for c in item_classes if 'level' in c]
                    if class_levels:
                        basic_info['data_zhiye'] = '|'.join(class_levels)
        except Exception as e:
            logger.warning(f"Error extracting item classes: {e}")
        
        # Extract weapon attack power (武器攻擊力)
        try:
            attack_element = soup.select_one('.basicList .ti:contains("武器攻擊力") + .con .conn')
            if attack_element:
                attack_text = attack_element.text.strip()
                basic_info['attack'] = attack_text
                basic_info['item_level'] = attack_text  # For compatibility with original format
        except Exception as e:
            logger.warning(f"Error extracting attack power: {e}")
            
        # Extract physical defense (AC)
        try:
            defense_element = soup.select_one('.basicList .ti:contains("物理防禦(AC)") + .con .conn')
            if defense_element:
                defense_text = defense_element.text.strip()
                basic_info['defense'] = defense_text
        except Exception as e:
            logger.warning(f"Error extracting defense: {e}")
            
        # Extract item stats (属性)
        try:
            stats_element = soup.select_one('.basicList .ti:contains("屬性") + .con .conn')
            if stats_element:
                stats_text = stats_element.get_text(separator="\n").strip()
                stats_list = [s.strip() for s in stats_text.split('\n') if s.strip()]
                basic_info['item_stats'] = stats_list
        except Exception as e:
            logger.warning(f"Error extracting item stats: {e}")
            
        # Extract blessed stats (祝福屬性)
        try:
            blessed_element = soup.select_one('.basicList .ti:contains("祝福屬性") + .con .conn')
            if blessed_element:
                blessed_text = blessed_element.get_text(separator="\n").strip()
                blessed_list = [s.strip() for s in blessed_text.split('\n') if s.strip()]
                basic_info['item_stats2'] = blessed_list
        except Exception as e:
            logger.warning(f"Error extracting blessed stats: {e}")
            
        # Extract material (材質)
        try:
            material_element = soup.select_one('.basicList .ti:contains("材質") + .con .conn')
            if material_element:
                material_text = material_element.text.strip()
                basic_info['material'] = material_text
        except Exception as e:
            logger.warning(f"Error extracting material: {e}")
            
        # Extract weight (重量)
        try:
            weight_element = soup.select_one('.basicList .ti:contains("重量") + .con .conn')
            if weight_element:
                weight_text = weight_element.text.strip()
                basic_info['weight'] = weight_text
        except Exception as e:
            logger.warning(f"Error extracting weight: {e}")
            
        return basic_info
        
    def extract_detail_info(self, soup):
        """
        Extract detailed information about the item
        """
        detail_info = {}
        
        # Extract damage protection (損傷)
        try:
            damage_element = soup.select_one('.detailInfo .xjList .ti:contains("損傷") + .con')
            if damage_element:
                damage_text = damage_element.text.strip()
                detail_info['canbedmg'] = damage_text
        except Exception as e:
            logger.warning(f"Error extracting damage protection: {e}")
            
        # Extract storage (倉庫)
        try:
            storage_element = soup.select_one('.detailInfo .xjList .ti:contains("倉庫") + .con')
            if storage_element:
                storage_text = storage_element.text.strip()
                detail_info['store'] = storage_text
        except Exception as e:
            logger.warning(f"Error extracting storage info: {e}")
            
        # Extract trade (交換)
        try:
            trade_element = soup.select_one('.detailInfo .xjList .ti:contains("交換") + .con')
            if trade_element:
                trade_text = trade_element.text.strip()
                detail_info['trade'] = trade_text
        except Exception as e:
            logger.warning(f"Error extracting trade info: {e}")
            
        # Extract safe value (安定值)
        try:
            safe_element = soup.select_one('.detailInfo .xjList .ti:contains("安定值") + .con')
            if safe_element:
                safe_text = safe_element.text.strip()
                detail_info['safe_val'] = safe_text
        except Exception as e:
            logger.warning(f"Error extracting safe value: {e}")
            
        return detail_info
        
    def extract_enhance_info(self, soup):
        """
        Extract enhancement information
        """
        enhance_info = []
        
        try:
            enhance_elements = soup.select('.addList .tbody li')
            for element in enhance_elements:
                columns = element.select('.column')
                if len(columns) >= 2:
                    level = columns[0].text.strip()
                    effect = columns[1].text.strip()
                    enhance_info.append({
                        'level': level,
                        'effect': effect
                    })
        except Exception as e:
            logger.warning(f"Error extracting enhancement info: {e}")
            
        return enhance_info
        
    def extract_monster_drops(self, soup):
        """
        Extract monster drops information
        """
        monster_drops = []
        
        # Try to find monster drops section - there might be none for this item
        try:
            monster_section = soup.select_one('.monsterInfo')
            if monster_section:
                monster_elements = monster_section.select('.monsInfo')
                for monster_elem in monster_elements:
                    monster_info = {}
                    
                    # Extract monster name and URL
                    name_elem = monster_elem.select_one('.monsName a')
                    if name_elem:
                        monster_info['monster_name'] = name_elem.text.strip()
                        monster_info['monster_url'] = name_elem.get('href', '')
                        if monster_info['monster_url'] and not monster_info['monster_url'].startswith('http'):
                            monster_info['monster_url'] = f"https://www.gametsg.net{monster_info['monster_url']}"
                        
                        # Extract monster ID from URL if possible
                        if 'monster_url' in monster_info:
                            id_match = re.search(r'id=(\d+)', monster_info['monster_url'])
                            if id_match:
                                monster_info['monster_id'] = id_match.group(1)
                    
                    # Extract monster type
                    type_elem = monster_elem.select_one('.monsType')
                    if type_elem:
                        monster_info['monster_type'] = type_elem.get('class', [''])[1] if len(type_elem.get('class', [])) > 1 else ''
                        monster_info['monster_size'] = type_elem.text.strip()
                    
                    # Extract monster size class
                    size_elem = monster_elem.select_one('.monsSize')
                    if size_elem:
                        size_class = size_elem.get('class', [''])[0] if size_elem.get('class', []) else ''
                        monster_info['monster_size_class'] = size_class
                    
                    # Extract monster level
                    level_elem = monster_elem.select_one('.monsLevel')
                    if level_elem:
                        monster_info['monster_level'] = level_elem.text.strip()
                    
                    # Extract monster weaknesses
                    weakness_elements = monster_elem.select('.monsPoint span')
                    if weakness_elements:
                        weaknesses = []
                        for elem in weakness_elements:
                            weakness = {
                                'type': elem.text.strip(),
                                'class': elem.get('class', [''])[0] if elem.get('class', []) else ''
                            }
                            weaknesses.append(weakness)
                        monster_info['monster_weaknesses'] = weaknesses
                    
                    # Extract monster areas
                    area_elements = monster_elem.select('.monsAddr li')
                    if area_elements:
                        areas = [elem.text.strip() for elem in area_elements if elem.text.strip()]
                        monster_info['monster_areas'] = areas
                    
                    monster_drops.append(monster_info)
        except Exception as e:
            logger.warning(f"Error extracting monster drops: {e}")
            
        return monster_drops
        
    def save_final_data(self):
        """
        Save the final data to final.json
        """
        try:
            logger.info(f"Saving final data to {self.output_path}")
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(self.final_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully saved {len(self.final_data)} items to {self.output_path}")
        except Exception as e:
            logger.error(f"Error saving final data: {e}")
    
    def process_and_update(self, item):
        """
        Process a single item and update the final data
        """
        # Fetch HTML content
        html_content = self.fetch_item_html(item)
        
        if html_content:
            # Parse the HTML content
            detailed_item = self.parse_item_html(html_content, item)
            
            if detailed_item:
                # Add to final data
                self.final_data.append(detailed_item)
                self.processed_count += 1
                
                # Save the final data every 10 items
                if self.processed_count % 10 == 0:
                    self.save_final_data()
                    logger.info(f"Progress: Processed {self.processed_count} items so far")
                
                # Save HTML to example folder (optional)
                self.save_html_example(item, html_content)
                
                return detailed_item
                
        return None
    
    def save_html_example(self, item, html_content):
        """
        Save HTML content to example folder for reference
        """
        if not html_content or not item.get('item_name'):
            return
            
        # Create example directory if it doesn't exist
        os.makedirs('example', exist_ok=True)
        
        # Create safe filename
        item_name = item.get('item_name', 'unknown')
        safe_name = re.sub(r'[\\/*?:"<>|]', '', item_name)
        
        # Save HTML to file
        file_path = os.path.join('example', f"{safe_name}.html")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            logger.warning(f"Error saving HTML example for {item_name}: {e}")
    
    def run(self):
        """
        Run the entire process
        """
        logger.info("Starting item fetcher")
        
        # Load the merge_items.json file
        items = self.load_merge_items()
        
        if not items:
            logger.error("No items found in merge_items.json. Exiting.")
            return
        
        # Check if final.json already exists and load it if it does
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    self.final_data = json.load(f)
                logger.info(f"Loaded {len(self.final_data)} items from existing {self.output_path}")
                
                # Create a map of existing items by ID
                existing_items = {item.get('item_id'): True for item in self.final_data if 'item_id' in item}
                
                # Filter out items that have already been processed
                items = [item for item in items if item.get('item_id') not in existing_items]
                logger.info(f"Found {len(items)} new items to process")
            except Exception as e:
                logger.error(f"Error loading existing final.json: {e}")
        
        # Process each item
        total_items = len(items)
        for i, item in enumerate(items):
            logger.info(f"Processing item {i+1}/{total_items}: {item.get('item_name', 'Unknown')}")
            self.process_and_update(item)
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
        
        # Save the final data one last time
        self.save_final_data()
        
        logger.info(f"Completed processing {self.processed_count} items")


if __name__ == "__main__":
    fetcher = ItemFetcher()
    fetcher.run()
