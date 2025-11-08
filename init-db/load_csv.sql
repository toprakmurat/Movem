-- Genres
\copy genres(id, genre_name) FROM '/docker-entrypoint-initdb.d/db_genres.csv' DELIMITER ',' CSV HEADER

-- platforms
\copy platforms(id, platform_name, logo_path) FROM '/docker-entrypoint-initdb.d/db_platforms.csv' DELIMITER ',' CSV HEADER

-- movie_platforms
\copy movie_platforms(movie_id, platform_id) FROM '/docker-entrypoint-initdb.d/movie_platforms.csv' DELIMITER ',' CSV HEADER

-- Movies 
\copy movies(id, title, overview, tagline, release_date, poster_file, banner_file, platform_id) FROM '/docker-entrypoint-initdb.d/db_movies.csv' DELIMITER ',' CSV HEADER

-- Movies_Genres
\copy movies_genres(movie_id, genre_id) FROM '/docker-entrypoint-initdb.d/db_movies_genres.csv' DELIMITER ',' CSV HEADER

-- comments
\copy comments(user_id, movie_id, body, rating, created_at, comment_likes, comment_dislikes) FROM '/docker-entrypoint-initdb.d/db_comments.csv' DELIMITER ',' CSV HEADER