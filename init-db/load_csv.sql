-- Users
\copy users(id, username, email, birth_date, password_hash, role, created_at, updated_at, game_score) FROM '/docker-entrypoint-initdb.d/db_genres.csv' DELIMITER ',' CSV HEADER

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

-- question_types
\copy question_types(id, question_type_name) FROM '/docker-entrypoint-initdb.d/db_question_types.csv' DELIMITER ',' CSV HEADER

-- statistic
\copy statistic(movie_id, revenue, runtime, vote_avg, vote_count, budget) FROM '/docker-entrypoint-initdb.d/db_statistic.csv' DELIMITER ',' CSV HEADER

-- movie_question
\copy movie_question(id, question_type, movie1_id, movie2_id) FROM '/docker-entrypoint-initdb.d/db_movie_question.csv' DELIMITER ',' CSV HEADER


