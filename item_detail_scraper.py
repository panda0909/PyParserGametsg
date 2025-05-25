import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import re
import time
from datetime import datetime

class ItemDetailScraper:
    def __init__(self, categories_json_path):
        """
        Initialize the scraper with the path to equipment categories JSON file
        """
        self.categories_json_path = categories_json_path
        self.base_url = "https://www.gametsg.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Create output directories if they don't exist
        self.output_dir = "scraped_data"
        self.json_dir = os.path.join(self.output_dir, "json")
        self.excel_dir = os.path.join(self.output_dir, "excel")
        
        for directory in [self.output_dir, self.json_dir, self.excel_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def load_categories(self):
        """
        Load equipment categories from the JSON file
        """
        try:
            with open(self.categories_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading categories: {str(e)}")
            return []
    
    def clean_text(self, text):
        """
        Clean text by removing extra spaces and newlines
        """
        if text is None:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def extract_item_data(self, li_element):
        """
        Extract data from a li element containing item information
        """
        try:
            # Initialize item data dictionary
            item_data = {
                "item_id": "",
                "item_name": "",
                "item_url": "",
                "item_image": "",
                "item_grade": "",
                "item_comment": "",
                "item_classes": [],
                "item_level": "",
                "item_stats": [],
                "data_zhiye": ""
            }
            
            # Get data-zhiye attribute
            item_data["data_zhiye"] = li_element.get('data-zhiye', '')
            
            # Get item image
            img_tag = li_element.select_one('.column img')
            if img_tag:
                item_data["item_image"] = self.base_url + img_tag.get('src', '')
              # Get item name, URL, grade and comment
            # Look for links with class that starts with "grade"
            item_link = li_element.select_one('.column a[class^="grade"]')
            if item_link:
                item_data["item_name"] = self.clean_text(item_link.get_text(strip=True).split('[')[0])
                item_data["item_url"] = self.base_url + item_link.get('href', '')
                
                # Extract grade from class name (e.g. grade032)
                classes = item_link.get('class', [])
                for cls in classes:
                    if cls.startswith('grade'):
                        item_data["item_grade"] = cls
                        break
                
                # Extract item ID from URL if available
                if 'id=' in item_link.get('href', ''):
                    item_data["item_id"] = item_link.get('href', '').split('id=')[-1]
                
                # Extract comment in square brackets if present
                comment_span = item_link.select_one('span.comment')
                if comment_span:
                    item_data["item_comment"] = self.clean_text(comment_span.text.strip('[]'))
            
            # Get character classes that can use this item
            class_spans = li_element.select('.column .class')
            if class_spans:
                for span in class_spans:
                    class_level = span.get('class', [])[1] if len(span.get('class', [])) > 1 else ""
                    class_name = self.clean_text(span.text)
                    item_data["item_classes"].append({
                        "name": class_name,
                        "level": class_level
                    })
            
            # Get item level
            level_column = li_element.select('.column')[3] if len(li_element.select('.column')) > 3 else None
            if level_column:
                item_data["item_level"] = self.clean_text(level_column.text)
            
            # Get item stats
            stats_column = li_element.select('.column')[-1] if li_element.select('.column') else None
            if stats_column and stats_column.find('p'):
                stats_text = stats_column.find('p').get_text(separator='\n')
                item_data["item_stats"] = [self.clean_text(line) for line in stats_text.split('\n') if self.clean_text(line)]
            
            return item_data
            
        except Exception as e:
            print(f"Error extracting item data: {str(e)}")
            return {}
    def scrape_category_page(self, category):
        """
        Scrape items from a category page
        """
        category_id = category["type_id"]
        category_name = category["category_name"]
        category_url = category["url"]
        
        print(f"\nScraping items for category: {category_name} (URL: {category_url})")
        
        try:
            response = requests.get(category_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the itemList div
            item_list_div = soup.find('div', class_='itemList')
            if not item_list_div:
                print(f"No itemList div found for category: {category_name}")
                return []
            
            # Find all li elements in the itemList div
            li_elements = item_list_div.find_all('li')
            if not li_elements:
                print(f"No items found in category: {category_name}")
                return []
            
            items = []
            for li in li_elements:
                item_data = self.extract_item_data(li)
                if item_data:
                    # Add category information
                    item_data["category_id"] = category_id
                    item_data["category_name"] = category_name
                    items.append(item_data)
                    print(f"  - Scraped item: {item_data['item_name']}")
            
            print(f"  Total items scraped: {len(items)}")
            return items
            
        except Exception as e:
            print(f"Error scraping category {category_name}: {str(e)}")
            return []
    
    def sanitize_filename(self, filename):
        """
        Sanitize filename by replacing invalid characters with underscores
        """
        if not filename:
            return "unnamed"
            
        # Replace common invalid filename characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\t', '\n', '\r']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Remove leading/trailing periods and spaces which can cause issues
        filename = filename.strip('. ')
        
        # Ensure the filename is not too long
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename
    def sanitize_filename(self, filename):
        """
        Sanitize filename by replacing invalid characters with underscores
        """
        if not filename:
            return "unnamed"
            
        # Replace common invalid filename characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\t', '\n', '\r']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Remove leading/trailing periods and spaces which can cause issues
        filename = filename.strip('. ')
        
        # Ensure the filename is not too long
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename
        
    def save_to_json(self, data, filename):
        """
        Save data to a JSON file
        """
        # Sanitize filename before saving
        safe_filename = self.sanitize_filename(filename)
        filepath = os.path.join(self.json_dir, safe_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} records to {filepath}")
    def save_to_excel(self, data, filename):
        """
        Save data to an Excel file
        """
        # Sanitize filename before saving
        safe_filename = self.sanitize_filename(filename)
        filepath = os.path.join(self.excel_dir, safe_filename)
        
        # Prepare data for Excel (flatten nested structures)
        excel_data = []
        for item in data:
            excel_item = item.copy()
            
            # Flatten classes list to comma-separated string
            if "item_classes" in excel_item:
                classes = [f"{cls['name']}({cls['level']})" for cls in excel_item["item_classes"]]
                excel_item["item_classes"] = ", ".join(classes)
            
            # Flatten stats list to newline-separated string
            if "item_stats" in excel_item:
                excel_item["item_stats"] = "\n".join(excel_item["item_stats"])
            
            excel_data.append(excel_item)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(excel_data)
        df.to_excel(filepath, index=False, engine='openpyxl')
        print(f"Saved {len(data)} records to {filepath}")
    
    def scrape_all_categories(self):
        """
        Scrape items from all categories
        """
        categories = self.load_categories()
        if not categories:
            print("No categories found. Please check the JSON file.")
            return
        
        print(f"Loaded {len(categories)} categories from {self.categories_json_path}")
        all_items = []
        
        for category in categories:
            items = self.scrape_category_page(category)
            if items:
                # Save category items to separate files
                category_name = self.sanitize_filename(category['category_name'])
                category_filename = f"items_{category['type_id']}_{category_name}"
                self.save_to_json(items, f"{category_filename}.json")
                self.save_to_excel(items, f"{category_filename}.xlsx")
                
                # Add to all items list
                all_items.extend(items)
            
            # Be nice to the server
            time.sleep(1)
          # Save all items to combined files
        if all_items:
            self.save_to_json(all_items, "all_items.json")
            self.save_to_excel(all_items, "all_items.xlsx")
        
        print(f"\nCompleted scraping. Total items collected: {len(all_items)}")

# Entry point
if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Starting item detail scraper at {start_time}")
    
    # Path to categories JSON file
    categories_json_path = "scraped_data/equipment_categories.json"
    
    scraper = ItemDetailScraper(categories_json_path)
    scraper.scrape_all_categories()
    
    end_time = datetime.now()
    print(f"Scraping completed at {end_time}")
    print(f"Total time: {end_time - start_time}")
