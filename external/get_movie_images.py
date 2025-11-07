import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm  

"""
This script fetches poster and banner images for movies in a CSV using the TMDB API,
saves them locally, and updates the CSV with the image paths.
"""


load_dotenv()

bearer_token = os.getenv("TMDB_BEARER_TOKEN")
image_base = os.getenv("BASE_URL")
poster_size = os.getenv("POSTER_SIZE", "w342")
banner_size = os.getenv("BANNER_SIZE", "w780")
images_dir = os.getenv("IMAGES_DIR", "images")      
output_csv = os.getenv("OUTPUT_CSV", "movies_with_images.csv")


df = pd.read_csv("./archive/tmdb_5000_movies.csv")
id_list = df["id"].tolist()

os.makedirs(images_dir, exist_ok=True)

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {bearer_token}"
}

poster_urls = []
banner_urls = []

RATE_LIMIT_DELAY = 0.35  

print("Starting")

for movie_id in tqdm(id_list, desc="Processing movies"):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
    params = {"include_image_language": "en,null"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Poster
            if data.get("posters"):
                poster_path = data["posters"][0]["file_path"].lstrip('/')
                poster_url = f"{image_base}/{poster_size}/{poster_path}"
                poster_filename = os.path.join(images_dir, os.path.basename(poster_path))

                if not os.path.exists(poster_filename):
                    img_data = requests.get(poster_url).content
                    with open(poster_filename, "wb") as f:
                        f.write(img_data)

                poster_urls.append(poster_path)
            else:
                poster_urls.append(None)

            # Banner
            if data.get("backdrops"):
                banner_path = data["backdrops"][0]["file_path"].lstrip('/')
                banner_url = f"{image_base}/{banner_size}/{banner_path}"
                banner_filename = os.path.join(images_dir, os.path.basename(banner_path))

                if not os.path.exists(banner_filename):
                    img_data = requests.get(banner_url).content
                    with open(banner_filename, "wb") as f:
                        f.write(img_data)

                banner_urls.append(banner_path)
            else:
                banner_urls.append(None)

        else:
            poster_urls.append(None)
            banner_urls.append(None)

        time.sleep(RATE_LIMIT_DELAY)

    except Exception as e:
        poster_urls.append(None)
        banner_urls.append(None)
        print(f"Error fetching movie {movie_id}: {e}")


df["poster_url"] = poster_urls
df["banner_url"] = banner_urls


df.to_csv(output_csv, index=False)

print("Finished")
