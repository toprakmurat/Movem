import requests
import time

image_urls = [
    "https://image.tmdb.org/t/p/w500/r3pPehX4ik8NLYPpbDRAh0YRtMb.jpg",
    "https://image.tmdb.org/t/p/w500/66RvLrRJTm4J8l3uHXWF09AICol.jpg",
    "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
    "https://image.tmdb.org/t/p/w500/a26cQPRhJPX6GbWfQbvZdrrp9j9.jpg",
    "https://image.tmdb.org/t/p/w500/14Cs3sr6nus6QTHThldis8p4Nlm.jpg",
    "https://image.tmdb.org/t/p/w500/yjMuqAyJUoQZGWsZ0vZuYj5inAR.jpg",
    "https://image.tmdb.org/t/p/w500/7Tmjr0jgVj8hHcd3UJD6HIilMKM.jpg",
    "https://image.tmdb.org/t/p/w500/ohXr0v9U0TfFu9IXbSDm5zoGV3R.jpg",
    "https://image.tmdb.org/t/p/w500/1yWmCAIGSVNuTOGyz9F48W9g1Ux.jpg",
    "https://image.tmdb.org/t/p/w500/eKZ07Ted7VHxQjbuZrRBFOamcKJ.jpg"
]

# Many prints included to see exact results clearly
def test_image_load_speed(urls):

    total_time = 0
    individual_times = []
    
    print(f"Testing a total of {len(urls)} image URLs...\n")
    
    for url in urls:
        try:
            start_time = time.time()
            response = requests.get(url) 
            end_time = time.time()
            duration = end_time - start_time

            individual_times.append(duration)
            total_time += duration
            
            if response.status_code == 200:
                print(f"[SUCCESS] URL: {url} \n    -> Load Time: {duration:.4f} seconds")
            else:
                print(f"[ERROR]   URL: {url} \n    -> Status Code: {response.status_code}, Time: {duration:.4f} seconds")

        except requests.exceptions.RequestException as e:
            print(f"[CRITICAL ERROR] URL: {url} \n    -> Error: {e}")
    
    print("\n--- PERFORMANCE SUMMARY ---")
    if individual_times:
        request_count = len(individual_times)
        average_time = total_time / request_count
        max_time = max(individual_times)
        
        print(f"Total number of tested images: {request_count}")
        print(f"Total time for all images (sequential): {total_time:.4f} seconds")
        print(f"Average load time per image: {average_time:.4f} seconds")
        print(f"Slowest image load time: {max_time:.4f} seconds")
        
        print("\nSummary to share with your friend:")
        print(f"-> Average load time per image: {average_time:.4f} seconds.")
        print(f"-> The slowest image loaded in {max_time:.4f} seconds.")
        
    else:
        print("No valid URLs to test.")

if __name__ == "__main__":
    test_image_load_speed(image_urls)
