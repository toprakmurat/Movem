-- Genres
\copy genres(id, genre_name) 
FROM '/docker-entrypoint-initdb.d/db_genres.csv' 
DELIMITER ',' 
CSV HEADER;

-- Movies 
\copy movies(id, title, overview, tagline, release_date, poster_file, banner_file, platform_id) 
FROM '/docker-entrypoint-initdb.d/db_movies.csv' 
DELIMITER ',' 
CSV HEADER;

-- Movies_Genres
\copy movies_genres(movie_id, genre_id) 
FROM '/docker-entrypoint-initdb.d/db_movies_genres.csv' 
DELIMITER ',' 
CSV HEADER;
