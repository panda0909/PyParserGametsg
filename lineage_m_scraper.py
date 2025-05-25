import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

class LineageMScraper:
    def __init__(self):
        self.base_url = "https://www.gametsg.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.item_list = []

    def get_equipment_categories(self):
        """
        Scrapes the main equipment page to find all equipment categories
        """
        try:
            url = f"{self.base_url}/equip.html"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that contain "/equip?type_name="
            links = soup.find_all('a', href=lambda href: href and '/equip?type_name=' in href)
            
            for link in links:
                type_name = link['href'].split('=')[-1]
                category_name = link.text.strip()
                
                item = {
                    'type_id': type_name,
                    'category_name': category_name,
                    'url': f"{self.base_url}{link['href']}"
                }
                
                self.item_list.append(item)
                print(f"Found category: {category_name} (ID: {type_name})")
            
            print(f"\nTotal categories found: {len(self.item_list)}")
            return self.item_list
                
        except Exception as e:
            print(f"Error getting equipment categories: {str(e)}")
            return []
    
    def save_categories_to_csv(self, filename="equipment_categories.csv"):
        """
        Saves the scraped categories to a CSV file
        """
        if not self.item_list:
            print("No categories to save. Please run get_equipment_categories() first.")
            return
            
        df = pd.DataFrame(self.item_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved {len(self.item_list)} categories to {filename}")

# Example usage
if __name__ == "__main__":
    scraper = LineageMScraper()
    categories = scraper.get_equipment_categories()
    scraper.save_categories_to_csv()
