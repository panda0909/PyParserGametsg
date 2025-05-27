import requests
import json
import os
import random
import time
from collections import defaultdict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('random_samples_fetcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RandomSamplesFetcher:
    def __init__(self, json_file_path, output_folder, samples_per_category=3):
        """
        Initialize the fetcher with the path to the items JSON file and output folder
        
        Args:
            json_file_path: Path to the merge_items.json file
            output_folder: Path to the example folder where HTML files will be saved
            samples_per_category: Number of random samples to select per category
        """
        self.json_file_path = json_file_path
        self.output_folder = output_folder
        self.samples_per_category = samples_per_category
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

    def load_json_data(self):
        """
        Load and parse the JSON file
        """
        logger.info(f"Loading JSON data from {self.json_file_path}")
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {len(data)} items")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON data: {e}")
            return []

    def group_by_category(self, items):
        """
        Group items by their category_name
        """
        category_groups = defaultdict(list)
        
        for item in items:
            category_name = item.get('category_name')
            if category_name:
                category_groups[category_name].append(item)
        
        logger.info(f"Found {len(category_groups)} different categories")
        return category_groups
        
    def select_random_samples(self, category_groups):
        """
        Select random samples from each category
        """
        random_samples = []
        
        for category, items in category_groups.items():
            # Select min(samples_per_category, len(items)) random samples
            num_samples = min(self.samples_per_category, len(items))
            samples = random.sample(items, num_samples)
            
            logger.info(f"Selected {num_samples} samples from category '{category}'")
            random_samples.extend(samples)
            
        return random_samples
        
    def fetch_and_save_html(self, samples):
        """
        Fetch HTML content for each sample and save to file
        """
        for item in samples:
            item_name = item.get('item_name', '')
            item_url = item.get('item_url', '')
            
            if not item_url or not item_name:
                logger.warning(f"Skipping item with no name or URL: {item}")
                continue
                
            # Create a valid filename from item_name
            safe_filename = self.create_safe_filename(item_name)
            output_path = os.path.join(self.output_folder, f"{safe_filename}.html")
            
            logger.info(f"Fetching HTML for item: {item_name} (URL: {item_url})")
            
            try:
                # Check if the file already exists
                if os.path.exists(output_path):
                    logger.info(f"File already exists: {output_path}, skipping")
                    continue
                    
                # Fetch the HTML content
                response = requests.get(item_url, headers=self.headers)
                response.raise_for_status()
                
                # Save the HTML content to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
                logger.info(f"Successfully saved HTML to {output_path}")
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching or saving HTML for {item_name}: {e}")
    
    def create_safe_filename(self, filename):
        """
        Create a safe filename from the item name
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        return filename
    
    def run(self):
        """
        Run the entire process
        """
        logger.info("Starting random samples fetcher")
        
        # Load JSON data
        items = self.load_json_data()
        if not items:
            logger.error("No items found. Exiting.")
            return
            
        # Group items by category
        category_groups = self.group_by_category(items)
        
        # Select random samples
        random_samples = self.select_random_samples(category_groups)
        
        # Fetch and save HTML for each sample
        self.fetch_and_save_html(random_samples)
        
        logger.info("Completed fetching random samples")


if __name__ == "__main__":
    # Path to the merge_items.json file
    json_file_path = os.path.join("scraped_data", "json", "merge_items.json")
    
    # Path to the example folder
    output_folder = "example"
    
    # Number of samples per category
    samples_per_category = 3
    
    # Run the fetcher
    fetcher = RandomSamplesFetcher(json_file_path, output_folder, samples_per_category)
    fetcher.run()
