

CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT NOT NULL,
    password varchar NOT NULL
    location varchar(50)
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
    state_id REFERENCES states
);


CREATE TABLE locations
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    city_id INTEGER REFERENCES cities ON DELETE CASCADE
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