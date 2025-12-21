-- Database and user are automatically created by Docker when starting with Docker Compose,
-- so we can directly connect to and use the 'movem' database
\c movem

------------------------------------------------------------
-- users table
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL CHECK (email LIKE '%@%'),
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
-- password_resets table (3NF normalization)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    reset_token VARCHAR(100) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    id SERIAL PRIMARY KEY,
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
    platform_id INTEGER REFERENCES platforms(id) ON DELETE SET NULL,
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
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    role VARCHAR(100),
    character_name VARCHAR(1024) DEFAULT 'Unknown',
    -- Same actor can play multiple roles in a movie
    -- Or, a director might play in a movie as an actor, too.
    -- To resolve this issue, character name is chosen to be ...
    -- ... a part of primary key as well.
    -- However, primary keys cannot be NULL, therefore it's ...
    -- ... defaulted to 'Unknown'
    PRIMARY KEY (movie_id, person_id, character_name)
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
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

------------------------------------------------------------
-- favorites table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id)
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
    has_spoiler BOOLEAN DEFAULT FALSE
);

------------------------------------------------------------
-- comment_votes table
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comment_votes (
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
    movie_id INTEGER PRIMARY KEY REFERENCES movies(id) ON DELETE CASCADE,
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
    list_id INTEGER REFERENCES user_lists(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (list_id, movie_id)
);