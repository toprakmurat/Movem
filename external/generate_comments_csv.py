import csv
import random
from datetime import datetime
import os

GOOD_COMMENTS = [
    "An absolute masterpiece! A must-watch for everyone.",
    "Breathtaking cinematography and flawless acting. 10/10.",
    "This movie changed my perspective. Simply brilliant.",
    "One of the best films I've seen in years. Highly recommended.",
    "A perfect movie. Everything from the plot to the score was amazing.",
    "Loved every minute of it. The ending was incredibly powerful.",
    "This will definitely be considered a classic.",
    "Incredible storytelling. I was hooked from start to finish.",
    "Visually stunning and emotionally resonant.",
    "Just... wow. I'm speechless. Go see it.",
    "Flawless execution. I can't find a single thing to criticize.",
    "The acting was phenomenal. A career-defining performance for the lead.",
    "The soundtrack will be stuck in my head for weeks. Incredible.",
    "I laughed, I cried. A true emotional rollercoaster.",
    "A brilliant script, perfectly brought to life. Bravo!"
]

NEUTRAL_COMMENTS = [
    "It was... okay. Not bad, but not great either.",
    "A decent film to pass the time. Don't expect a masterpiece.",
    "Had a really interesting premise, but the execution was a bit lacking.",
    "I'm mixed on this one. Some parts were great, others dragged on.",
    "Watchable. It's exactly what you'd expect, nothing more, nothing less.",
    "I can see why some people like it, but it just wasn't for me.",
    "An average movie. Good for a lazy Sunday.",
    "The plot was a bit predictable, but the acting saved it.",
    "Not memorable, but not terrible. It's fine.",
    "I neither loved it nor hated it.",
    "The first half was much stronger than the second.",
    "Visually, it was nice, but the story didn't really go anywhere.",
    "A solid rental, but I wouldn't rush to the cinema for it.",
    "It's... a movie. It exists. I watched it.",
    "The ending felt rushed, but the journey was okay."
]

BAD_COMMENTS = [
    "A complete waste of time. I want my two hours back.",
    "One of the worst movies I've ever seen. Avoid at all costs.",
    "The plot was incoherent and full of holes.",
    "Terrible acting and an even worse script.",
    "I fell asleep halfway through. Incredibly boring.",
    "How did this even get made? It's awful.",
    "I don't understand the good reviews. This was just bad.",
    "The characters made no sense and the dialogue was cringeworthy.",
    "I regret watching this. So disappointing.",
    "Just... no. Save your money and watch something else.",
    "The special effects looked cheap and unfinished.",
    "I've seen student films with better writing than this.",
    "It's clear the director had no idea what they were doing.",
    "All style and no substance. A hollow, boring film.",
    "I actually felt insulted watching this. It's that bad."
]

INPUT_CSV_PATH = 'src/data/tmdb_5000_movies.csv'
OUTPUT_CSV_PATH = 'init-db/db_comments.csv'

os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

comments_to_write = []

print("Comment generation script started...")
print(f"Reading movies from: {INPUT_CSV_PATH}")

try:
    with open(INPUT_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        movie_count = 0
        for row in reader:
            movie_count += 1
            try:
                movie_id = int(row['id'])
                rating_str = row.get('vote_average')
                
                rating = float(rating_str) if rating_str and rating_str != '0.0' else 5.0
                rating_int = int(round(rating))

                num_comments = random.randint(1, 3)

                for _ in range(num_comments):
                    user_id = random.randint(1, 100) 
                    
                    if rating >= 7.5:
                        body = random.choice(GOOD_COMMENTS)
                    elif rating >= 5.0:
                        body = random.choice(NEUTRAL_COMMENTS)
                    else:
                        body = random.choice(BAD_COMMENTS)
                    
                    comment_likes = random.randint(0, 100)
                    comment_dislikes = random.randint(0, 50)
                    created_at = datetime.now()
                    
                    comments_to_write.append([
                        user_id, 
                        movie_id, 
                        body, 
                        rating_int, 
                        created_at, 
                        comment_likes, 
                        comment_dislikes
                    ])
                    
            except (ValueError, TypeError):
                print(f"Skipping corrupt row (Movie ID: {row.get('id')})")
                continue
    
    print(f"Generated {len(comments_to_write)} total comments for {movie_count} movies.")

    print(f"Writing comments to: {OUTPUT_CSV_PATH}...")
    
    HEADERS = [
        'user_id', 
        'movie_id', 
        'body', 
        'rating', 
        'created_at', 
        'comment_likes', 
        'comment_dislikes'
    ]
    
    with open(OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(comments_to_write)
        
    print(f"Successfully created {OUTPUT_CSV_PATH}!")
    print("\nScript finished. You can now add 'db_comments.csv' to your 'load_csv.sql' file.")

except FileNotFoundError:
    print(f"FATAL ERROR: Input file not found at {INPUT_CSV_PATH}")
except Exception as e:
    print(f"An error occurred: {e}")