import os
import time
import requests 
import csv
from dotenv import load_dotenv

load_dotenv() 

API_KEY = os.environ.get('TMDB_API_KEY')
API_BASE_URL = "https://api.themoviedb.org/3"

if not API_KEY:
    print("FATAL ERROR: TMDB_API_KEY .env dosyanızda bulunamadı.")
    exit(1)

def fetch_watch_provider(movie_id):
    try:
        url = f"{API_BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        providers = data.get('results', {}).get('US', {}).get('flatrate', [])
        
        if providers:
            sorted_providers = sorted(providers, key=lambda p: p.get('display_priority', 99))
            best_provider = sorted_providers[0] 
            
            return {
                "name": best_provider.get('provider_name'),
                "logo_path": best_provider.get('logo_path'),
                "id": best_provider.get('provider_id')
            }
    except Exception:
        pass
    return None

movies_csv_path = './init-db/db_movies.csv'
unique_platforms = {}
movie_platform_relations = []

print("Script started. Reading base movies CSV...")

try:
    with open(movies_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        movie_ids = [row['id'] for row in reader]

    print(f"Found {len(movie_ids)} movies. Starting API calls... (This will take a long time!)")

    for i, movie_id in enumerate(movie_ids):
        if (i + 1) % 100 == 0:
            print(f"  > Processing movie {i+1}/{len(movie_ids)}...")

        provider_info = fetch_watch_provider(movie_id)
        
        if provider_info:
            platform_id = provider_info['id']
            platform_name = provider_info['name']
            logo_path = provider_info['logo_path']
            
            if platform_id not in unique_platforms:
                unique_platforms[platform_id] = (platform_name, logo_path)
            
            movie_platform_relations.append((movie_id, platform_id))

        time.sleep(0.25)

    print(f"API processing complete. Found {len(unique_platforms)} unique platforms.")

    platforms_output_path = './init-db/platforms.csv'
    print(f"Writing {platforms_output_path}...")
    with open(platforms_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'platform_name', 'logo_path'])
        for platform_id, (name, logo) in unique_platforms.items():
            writer.writerow([platform_id, name, logo])

    relation_output_path = './init-db/movie_platforms.csv'
    print(f"Writing {relation_output_path}...")
    with open(relation_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['movie_id', 'platform_id'])
        writer.writerows(movie_platform_relations)

    print("All CSV files generated successfully!")

except Exception as e:
    print(f"An error occurred: {e}")