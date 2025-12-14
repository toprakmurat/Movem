-- Users
\copy users(id, username, email, first_name, last_name, bio, birth_date, password_hash, role, created_at, updated_at, game_score, profile_picture) FROM '/docker-entrypoint-initdb.d/csv/db_users.csv' DELIMITER ',' CSV HEADER;
-- Genres
\copy genres(id, genre_name) FROM '/docker-entrypoint-initdb.d/csv/db_genres.csv' DELIMITER ',' CSV HEADER

-- platforms
\copy platforms(id, platform_name, logo_path) FROM '/docker-entrypoint-initdb.d/csv/db_platforms.csv' DELIMITER ',' CSV HEADER

-- Movies 
\copy movies(id, title, overview, tagline, release_date, poster_file, banner_file, platform_id) FROM '/docker-entrypoint-initdb.d/csv/db_movies.csv' DELIMITER ',' CSV HEADER

-- people
\copy people(id, name, biography, birth_date, photo_url, created_at) FROM '/docker-entrypoint-initdb.d/csv/db_people.csv' DELIMITER ',' CSV HEADER

-- movie_cast
\copy movie_cast(id, movie_id, person_id, role, character_name) FROM '/docker-entrypoint-initdb.d/csv/db_movie_cast.csv' DELIMITER ',' CSV HEADER

-- Movies_Genres
\copy movies_genres(movie_id, genre_id) FROM '/docker-entrypoint-initdb.d/csv/db_movies_genres.csv' DELIMITER ',' CSV HEADER

-- comments
\copy comments(user_id, movie_id, body, rating, created_at, comment_likes, comment_dislikes) FROM '/docker-entrypoint-initdb.d/csv/db_comments.csv' DELIMITER ',' CSV HEADER

-- question_types
\copy question_types(id, question_type_name) FROM '/docker-entrypoint-initdb.d/csv/db_question_types.csv' DELIMITER ',' CSV HEADER

-- statistic
\copy statistic(movie_id, revenue, runtime, vote_avg, vote_count, budget) FROM '/docker-entrypoint-initdb.d/csv/db_statistic.csv' DELIMITER ',' CSV HEADER

-- movie_question
\copy movie_question(id, question_type, movie1_id, movie2_id) FROM '/docker-entrypoint-initdb.d/csv/db_movie_question.csv' DELIMITER ',' CSV HEADER

SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
