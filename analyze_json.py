import json
import os

def analyze_json_file(file_path):
    """Analyze a JSON file and print statistics"""
    try:
        # Get file size in KB
        file_size_kb = os.path.getsize(file_path) / 1024
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count items
        item_count = len(data)
        
        print(f"File path: {file_path}")
        print(f"File size: {file_size_kb:.2f} KB")
        print(f"Number of items: {item_count}")
        
        # Count items with non-empty names
        items_with_names = sum(1 for item in data if item.get('item_name', '') != '')
        print(f"Items with non-empty names: {items_with_names}")
        
        # Get sample of first 3 item names
        sample_names = [item.get('item_name', '') for item in data[:3] if item.get('item_name', '') != '']
        print(f"Sample item names: {', '.join(sample_names[:3])}")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    # Define the JSON file to analyze
    json_file = os.path.join('scraped_data', 'json', 'nonempty_name_items.json')
    
    # Analyze the file
    analyze_json_file(json_file)
