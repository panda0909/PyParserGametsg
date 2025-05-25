import json
import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_json_file(file_path):
    """
    Fix JSON file by removing invalid characters and correcting format issues
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove invalid characters
        content = re.sub(r'[^\x00-\x7F\u0080-\uFFFF]', '', content)
        
        # Fix common JSON format issues
        content = content.replace('ㄈ"', '"')  # Fix specific issue with "ㄈ" character
        
        # Try to parse the JSON to ensure it's valid
        try:
            json_data = json.loads(content)
            logger.info(f"Successfully parsed JSON after fixes")
        except json.JSONDecodeError as e:
            logger.error(f"JSON still invalid after fixes: {str(e)}")
            return False
        
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully fixed and saved JSON file: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing JSON file {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    # Path to the JSON file that needs fixing
    json_file_path = "scraped_data/json/all_items.json"
    
    logger.info(f"Attempting to fix JSON file: {json_file_path}")
    result = fix_json_file(json_file_path)
    
    if result:
        logger.info("JSON file fixed successfully")
    else:
        logger.error("Failed to fix JSON file")
