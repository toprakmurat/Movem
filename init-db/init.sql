-- Database and user are automatically created by Docker when starting with Docker Compose,
-- so we can directly connect to and use the 'movem' database
\c movem

------------------------------------------------------------
-- users table
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    bio TEXT,
    birth_date DATE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    game_score INTEGER,
    profile_picture VARCHAR(255) DEFAULT 'img/placeholder_avatar.svg'
);

------------------------------------------------------------
-- question_types table
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS question_types (
    id SERIAL PRIMARY KEY,
    question_type_name VARCHAR(50)
);
------------------------------------------------------------
-- platforms table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY,
    platform_name VARCHAR(100),
    logo_path VARCHAR(256)
);

------------------------------------------------------------
-- movies table 
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movies(
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    overview TEXT,
    tagline  VARCHAR(256),
    release_date DATE,
    poster_file VARCHAR(100),
    banner_file VARCHAR(100),
    platform_id INTEGER REFERENCES platforms(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- people table (actors, directors)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY,
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
    character_name VARCHAR(1024)
);

------------------------------------------------------------
-- genres table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
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
    body TEXT,
    rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    comment_likes INTEGER,
    comment_dislikes INTEGER,
    has_spoiler BOOLEAN DEFAULT FALSE
);

------------------------------------------------------------
-- comment_votes table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comment_votes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    vote_type VARCHAR(10) CHECK (vote_type IN ('like', 'dislike')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, comment_id)
);

------------------------------------------------------------
-- statistic table 
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS statistic (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER UNIQUE REFERENCES movies(id) ON DELETE CASCADE,
    revenue BIGINT,
    runtime NUMERIC,
    vote_avg NUMERIC(4,1), -- to store ratings avg from 0,0 to 10,0
    vote_count INTEGER,
    budget BIGINT
);

------------------------------------------------------------
-- movie_question table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movie_question (
    id SERIAL PRIMARY KEY,
    question_type INTEGER REFERENCES question_types(id) ON DELETE CASCADE,   -- 'higher_budget', 'more_awards' etc
    movie1_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    movie2_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- people_question table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people_question (
    id SERIAL PRIMARY KEY,
    question_type INTEGER REFERENCES question_types(id) ON DELETE CASCADE,   -- 'has more movie', 'age' etc
    actor1_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    actor2_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
------------------------------------------------------------
-- user_lists table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    list_name VARCHAR(100) NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- list_items table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS list_items (
    id SERIAL PRIMARY KEY,
    list_id INTEGER REFERENCES user_lists(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(list_id, movie_id)
);