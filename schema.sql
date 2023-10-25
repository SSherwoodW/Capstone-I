\c moveIn

CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    location varchar(50),
    password varchar(30) NOT NULL
);

CREATE TABLE states 
(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state_code varchar(2) NOT NULL
);

CREATE TABLE cities
(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state_id INTEGER REFERENCES states(id)
);


CREATE TABLE locations
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE
    address varchar(150) NOT NULL,
    search_radius INTEGER NOT NULL
);

CREATE TABLE saved_searches
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations ON DELETE CASCADE,
    rent_avg INTEGER NOT NULL,
    buy_avg INTEGER NOT NULL,
    crime_score FLOAT
);

CREATE TABLE reviews
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations ON DELETE CASCADE,
    rating FLOAT NOT NULL,
    review_body varchar(300)
)