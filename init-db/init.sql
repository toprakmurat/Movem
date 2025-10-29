-- Database and user are automatically created by Docker when starting with Docker Compose,
-- so we can directly connect to and use the 'movem' database
\c movem


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
    platform_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

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