CREATE TABLE IF NOT EXISTS tracks_raw (
    track_id VARCHAR(255) PRIMARY KEY,
    track_name VARCHAR(255),
    energy FLOAT,
    track_genre VARCHAR(255),
    artist1 VARCHAR(255),
    artist2 VARCHAR(255),
    artist3 VARCHAR(255),
    artist4 VARCHAR(255)
);
