import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import json
from datetime import datetime

class LineageMScraper:
    def __init__(self):
        self.base_url = "https://www.gametsg.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.categories = []
        self.items = []
        
        # Create output directory if it doesn't exist
        self.output_dir = "scraped_data"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_equipment_categories(self):
        """
        Scrapes the main equipment page to find all equipment categories
        """
        try:
            url = f"{self.base_url}/equip.html"
            print(f"Fetching categories from {url}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that contain "/equip?type_name="
            links = soup.find_all('a', href=lambda href: href and '/equip?type_name=' in href)
            
            for link in links:
                type_name = link['href'].split('=')[-1]
                category_name = link.text.strip()
                
                category = {
                    'type_id': type_name,
                    'category_name': category_name,
                    'url': f"{self.base_url}{link['href']}"
                }
                
                self.categories.append(category)
                print(f"Found category: {category_name} (ID: {type_name})")
            
            print(f"\nTotal categories found: {len(self.categories)}")
            
            # Save categories
            self._save_to_csv(self.categories, "equipment_categories.csv")
            self._save_to_json(self.categories, "equipment_categories.json")
            
            return self.categories
                
        except Exception as e:
            print(f"Error getting equipment categories: {str(e)}")
            return []

    def get_items_for_category(self, category):
        """
        Scrapes items for a specific category
        """
        try:
            category_id = category['type_id']
            category_name = category['category_name']
            url = category['url']
            
            print(f"\nScraping items for category: {category_name} (URL: {url})")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table containing the items
            item_table = soup.find('table', class_='table')
            if not item_table:
                print(f"No item table found for category: {category_name}")
                return []
                
            rows = item_table.find_all('tr')[1:]  # Skip header row
            category_items = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                # Get item details
                item_name = cells[0].text.strip()
                
                # Check if there's an item detail link
                item_link = cells[0].find('a', href=True)
                item_url = f"{self.base_url}{item_link['href']}" if item_link else None
                
                item_data = {
                    'category_id': category_id,
                    'category_name': category_name,
                    'item_name': item_name,
                    'item_url': item_url
                }
                
                # Add other cells as available
                for i, cell in enumerate(cells[1:], 1):
                    key = f"attribute_{i}"
                    value = cell.text.strip()
                    item_data[key] = value
                
                category_items.append(item_data)
                print(f"Found item: {item_name}")
            
            # Add items to the main list
            self.items.extend(category_items)
            
            print(f"Found {len(category_items)} items in category {category_name}")
            
            # Be nice to the server
            time.sleep(1)
            
            return category_items
        
        except Exception as e:
            print(f"Error scraping items for category {category['category_name']}: {str(e)}")
            return []

    def scrape_all_categories(self):
        """
        Scrapes items for all categories
        """
        if not self.categories:
            self.get_equipment_categories()
        
        for category in self.categories:
            items = self.get_items_for_category(category)
            
            # Save items for this category
            category_filename = f"items_{category['type_id']}_{self._sanitize_filename(category['category_name'])}"
            self._save_to_csv(items, f"{category_filename}.csv")
            self._save_to_json(items, f"{category_filename}.json")
        
        # Save all items
        self._save_to_csv(self.items, "all_items.csv")
        self._save_to_json(self.items, "all_items.json")
        
        print(f"\nCompleted scraping. Total items collected: {len(self.items)}")

    def _save_to_csv(self, data, filename):
        """
        Saves data to a CSV file
        """
        if not data:
            print(f"No data to save to {filename}")
            return
            
        filepath = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Saved {len(data)} records to {filepath}")

    def _save_to_json(self, data, filename):
        """
        Saves data to a JSON file
        """
        if not data:
            print(f"No data to save to {filename}")
            return
            
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} records to {filepath}")
    
    def _sanitize_filename(self, filename):
        """
        Sanitizes a string to be used as a filename
        """
        # Replace invalid filename characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

# Example usage
if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Starting scraper at {start_time}")
    
    scraper = LineageMScraper()
    scraper.get_equipment_categories()
    scraper.scrape_all_categories()
    
    end_time = datetime.now()
    print(f"Scraping completed at {end_time}")
    print(f"Total time: {end_time - start_time}")
