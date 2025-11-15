import csv
import json
from datetime import datetime

def create_people_csv(source_csv, output_csv='people.csv'):
    """Create people.csv from the TMDB credits CSV."""
    people_dict = {}  # Prevent duplicate persons
    
    with open(source_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            cast_json = row.get('cast', '[]')
            crew_json = row.get('crew', '[]')
            
            try:
                cast_list = json.loads(cast_json)
            except json.JSONDecodeError:
                cast_list = []
            
            try:
                crew_list = json.loads(crew_json)
            except json.JSONDecodeError:
                crew_list = []
            
            # Cast (first 15 people per movie)
            for cast_member in cast_list[:15]:
                person_id = cast_member.get('id')
                person_name = cast_member.get('name', '')
                
                if person_id and person_id not in people_dict:
                    people_dict[person_id] = {
                        'id': person_id,
                        'name': person_name,
                        'biography': '',
                        'birth_date': '',
                        'photo_url': '',
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            # Directors only
            for crew_member in crew_list:
                if crew_member.get('job') == 'Director':
                    person_id = crew_member.get('id')
                    person_name = crew_member.get('name', '')
                    
                    if person_id and person_id not in people_dict:
                        people_dict[person_id] = {
                            'id': person_id,
                            'name': person_name,
                            'biography': '',
                            'birth_date': '',
                            'photo_url': '',
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'biography', 'birth_date', 'photo_url', 'created_at']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for person in people_dict.values():
            writer.writerow(person)
    
    print(f"Created {output_csv} with {len(people_dict)} people")
    return len(people_dict)

def create_movie_cast_csv(source_csv, output_csv='movie_cast.csv'):
    """Create movie_cast.csv (actors + directors)."""
    cast_entries = []
    cast_id = 1
    
    with open(source_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            movie_id = row.get('movie_id', '')
            
            try:
                cast_list = json.loads(row.get('cast', '[]'))
            except json.JSONDecodeError:
                cast_list = []
            
            try:
                crew_list = json.loads(row.get('crew', '[]'))
            except json.JSONDecodeError:
                crew_list = []
            
            # Actors (first 15)
            for cast_member in cast_list[:15]:
                person_id = cast_member.get('id')
                character_name = cast_member.get('character', '')
                
                if person_id:
                    cast_entries.append({
                        'id': cast_id,
                        'movie_id': movie_id,
                        'person_id': person_id,
                        'role': 'Actor',
                        'character_name': character_name
                    })
                    cast_id += 1
            
            # Director entries
            for crew_member in crew_list:
                if crew_member.get('job') == 'Director':
                    person_id = crew_member.get('id')
                    
                    if person_id:
                        cast_entries.append({
                            'id': cast_id,
                            'movie_id': movie_id,
                            'person_id': person_id,
                            'role': 'Director',
                            'character_name': ''
                        })
                        cast_id += 1
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'movie_id', 'person_id', 'role', 'character_name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in cast_entries:
            writer.writerow(entry)
    
    print(f"Created {output_csv} with {len(cast_entries)} cast entries")
    return len(cast_entries)

def transform_csv_to_db_format(source_csv):
    """Transform source TMDB CSV into normalized DB CSV files."""
    print("Transforming CSV to database-compliant format...")
    print("-" * 60)
    
    people_count = create_people_csv(source_csv)
    cast_count = create_movie_cast_csv(source_csv)
    
if __name__ == "__main__":
    transform_csv_to_db_format("tmdb_5000_credits.csv")
