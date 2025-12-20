-- Users
\copy users(id, username, email, first_name, last_name, bio, birth_date, password_hash, role, created_at, updated_at, game_score, profile_picture) FROM '/docker-entrypoint-initdb.d/csv/db_users.csv' DELIMITER ',' CSV HEADER;
-- Genres
\copy genres(id, genre_name) FROM '/docker-entrypoint-initdb.d/csv/db_genres.csv' DELIMITER ',' CSV HEADER

-- platforms
\copy platforms(id, platform_name, logo_path) FROM '/docker-entrypoint-initdb.d/csv/db_platforms.csv' DELIMITER ',' CSV HEADER

-- Movies 
\copy movies(id, title, overview, tagline, release_date, poster_file, banner_file, platform_id) FROM '/docker-entrypoint-initdb.d/csv/db_movies.csv' DELIMITER ',' CSV HEADER

-- Favorites
\copy favorites(user_id, movie_id) FROM '/docker-entrypoint-initdb.d/csv/db_favorites.csv' DELIMITER ',' CSV HEADER

-- people
\copy people(id, name, biography, birth_date, photo_url, created_at) FROM '/docker-entrypoint-initdb.d/csv/db_people.csv' DELIMITER ',' CSV HEADER

-- movie_cast
\copy movie_cast(id, movie_id, person_id, role, character_name) FROM '/docker-entrypoint-initdb.d/csv/db_movie_cast.csv' DELIMITER ',' CSV HEADER

-- Movies_Genres
\copy movies_genres(movie_id, genre_id) FROM '/docker-entrypoint-initdb.d/csv/db_movies_genres.csv' DELIMITER ',' CSV HEADER

-- comments
\copy comments(user_id, movie_id, body, rating, created_at, comment_likes, comment_dislikes) FROM '/docker-entrypoint-initdb.d/csv/db_comments.csv' DELIMITER ',' CSV HEADER

-- Comment Votes
\copy comment_votes(user_id, comment_id, vote_type) FROM '/docker-entrypoint-initdb.d/csv/db_comment_votes.csv' DELIMITER ',' CSV HEADER

-- question_types
\copy question_types(id, question_type_name) FROM '/docker-entrypoint-initdb.d/csv/db_question_types.csv' DELIMITER ',' CSV HEADER

-- statistic
\copy statistic(movie_id, revenue, runtime, vote_avg, vote_count, budget) FROM '/docker-entrypoint-initdb.d/csv/db_statistic.csv' DELIMITER ',' CSV HEADER

-- movie_question
\copy movie_question(id, question_type, movie1_id, movie2_id) FROM '/docker-entrypoint-initdb.d/csv/db_movie_question.csv' DELIMITER ',' CSV HEADER

-- user_lists
\copy user_lists(id, user_id, list_name, is_public, created_at) FROM '/docker-entrypoint-initdb.d/csv/db_user_lists.csv' DELIMITER ',' CSV HEADER

-- list_items
\copy list_items(id, list_id, movie_id, added_at) FROM '/docker-entrypoint-initdb.d/csv/db_list_items.csv' DELIMITER ',' CSV HEADER


SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

SELECT setval('user_lists_id_seq', (SELECT MAX(id) FROM user_lists));

SELECT setval('list_items_id_seq', (SELECT MAX(id) FROM list_items));


SELECT setval('movie_question_id_seq', (SELECT MAX(id) FROM movie_question));

SELECT setval('question_types_id_seq', (SELECT MAX(id) FROM question_types));


-- Create Indexes 

-- Index for title search
CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
-- Index for finding movies by platform 
CREATE INDEX IF NOT EXISTS idx_movies_platform_id ON movies(platform_id);
-- Index for finding movies by genre 
CREATE INDEX IF NOT EXISTS idx_movies_genres_genre_id ON movies_genres(genre_id);
-- Index for finding who favorited a movie 
CREATE INDEX IF NOT EXISTS idx_favorites_movie_id ON favorites(movie_id);

