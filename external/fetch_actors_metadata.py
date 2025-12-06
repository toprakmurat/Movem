import csv
import os
import asyncio
import aiohttp
import time


TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/person/{}?language=en-US"

INPUT_FILE = "db_people.csv"
OUTPUT_FILE = "filled_db_people.csv"

# Simple throttle: 1 request every 3 seconds
REQUEST_DELAY = 0.3


async def fetch_person(session, person_id, max_retries=3):
    """Fetch TMDB person data, one request every 3 seconds."""
    url = BASE_URL.format(person_id)
    params = {"api_key": TMDB_API_KEY}

    for attempt in range(max_retries):
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    # Wait 3 seconds before next request
                    await asyncio.sleep(REQUEST_DELAY)

                    return data
                else:
                    print(f"ID {person_id} -> HTTP {resp.status}")
                    return None

        except aiohttp.ClientError as e:
            print(f"Network error for ID {person_id}: {e}")

        # retry with exponential backoff
        await asyncio.sleep(0.5 * (2 ** attempt))

    print(f"Failed to fetch ID {person_id} after retries.")
    return None


async def process_all(actors):
    """Fetch all actors sequentially, 1 request every 3 seconds."""
    async with aiohttp.ClientSession(headers={"accept": "application/json"}) as session:
        filled_rows = []

        for row in actors:
            person_id = row["id"]
            print(f"Fetching {person_id}...")

            data = await fetch_person(session, person_id)

            if data:
                row["biography"] = data.get("biography", "")
                row["birth_date"] = data.get("birthday", "")
                row["photo_url"] = data.get("profile_path", "")

            filled_rows.append(row)

        return filled_rows


def main():
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actors = list(reader)

    filled_rows = asyncio.run(process_all(actors))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filled_rows[0].keys())
        writer.writeheader()
        writer.writerows(filled_rows)

    print(f"\nDone! Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
