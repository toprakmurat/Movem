import os
import csv
import requests
import time

SOURCE_CSV_FILE = 'init-db/db_platforms.csv'
IMAGE_SAVE_DIR = 'images/platforms'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w200'

os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
print(f"Images will be saved to: {IMAGE_SAVE_DIR}")

downloaded_count = 0
skipped_count = 0
failed_count = 0

try:
    with open(SOURCE_CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        if 'logo_path' not in reader.fieldnames:
            print(f"FATAL ERROR: 'logo_path' column not found in {SOURCE_CSV_FILE}")
            exit(1)
            
        platform_rows = list(reader)
        total_platforms = len(platform_rows)
        print(f"Found {total_platforms} platforms in CSV file.")

        for i, row in enumerate(platform_rows):
            logo_path = row['logo_path']
            platform_name = row['platform_name']
            
            if not logo_path or logo_path == 'N/A':
                print(f"({i+1}/{total_platforms}) Skipping '{platform_name}' (No logo path)")
                skipped_count += 1
                continue

            full_image_url = f"{IMAGE_BASE_URL}{logo_path}"
            local_filename = os.path.basename(logo_path)
            local_save_path = os.path.join(IMAGE_SAVE_DIR, local_filename)

            if os.path.exists(local_save_path):
                skipped_count += 1
                continue
            
            try:
                response = requests.get(full_image_url, timeout=10)
                response.raise_for_status()

                with open(local_save_path, 'wb') as img_file:
                    img_file.write(response.content)
                
                print(f"({i+1}/{total_platforms}) SUCCESS: Downloaded {local_filename} (for {platform_name})")
                downloaded_count += 1
                
                time.sleep(0.1) 

            except requests.exceptions.RequestException as e:
                print(f"({i+1}/{total_platforms}) ERROR downloading {full_image_url}: {e}")
                failed_count += 1

except FileNotFoundError:
    print(f"FATAL ERROR: Source file not found at {SOURCE_CSV_FILE}")
    print("Please run 'generate_platform_csvs.py' script first to create this file.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")