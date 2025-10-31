-- Database and user are automatically created by Docker when starting with Docker Compose,
-- so we can directly connect to and use the 'movem' database
\c movem


------------------------------------------------------------
-- platforms table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platforms (
    id SERIAL PRIMARY KEY,
    platform_name VARCHAR(100),
    logo_path VARCHAR(256)
);

------------------------------------------------------------
-- movies table 
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movies(
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    overview TEXT,
    tagline  VARCHAR(256),
    release_date DATE,
    poster_url VARCHAR(100),
    platform_id INTEGER REFERENCES platforms(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- people table (actors, directors)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    biography TEXT,
    birth_date DATE,
    photo_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- movie_cast table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movie_cast (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    role VARCHAR(100),
    character_name VARCHAR(255)
);

------------------------------------------------------------
-- genres table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL
);

------------------------------------------------------------
-- movies_genres table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movies_genres (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE
);

------------------------------------------------------------
-- favorites table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- comments table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comment_likes INTEGER,
    comment_dislikes INTEGER
);

------------------------------------------------------------
-- statistic table 
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS statistic (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER UNIQUE REFERENCES movies(id) ON DELETE CASCADE,
    revenue BIGINT,
    runtime INTEGER,
    vote_avg NUMERIC(4,1), -- to store ratings avg from 0,0 to 10,0
    vote_count INTEGER,
    budget BIGINT
);

------------------------------------------------------------
-- movie_question table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movie_question (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(50),   -- 'higher_budget', 'more_awards' etc
    movie1_id INTEGER UNIQUE REFERENCES movies(id) ON DELETE CASCADE,
    movie2_id INTEGER UNIQUE REFERENCES movies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- people_question table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people_question (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(50),   -- 'has more movie', 'age' etc
    actor1_id INTEGER UNIQUE REFERENCES people(id) ON DELETE CASCADE,
    actor2_id INTEGER UNIQUE REFERENCES people(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);