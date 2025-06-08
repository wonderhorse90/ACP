-- DATA CLEANING 
SELECT *
FROM tracks_raw;

UPDATE tracks_raw
SET track_genre = 'singer'
WHERE track_genre = 'singer-songwriter';

ALTER TABLE tracks
RENAME TO tracks_raw;

SELECT track_id,
		track_name,
		energy,
		STRING_AGG(track_genre, ',') AS genre,
		CONCAT_WS(',', artist1, artist2, artist3,artist4)
	FROM tracks_raw
	GROUP BY track_id, track_name, energy, artist1, artist2, artist3, artist4;

-- CREATE A NEW TRACK TABLE THAT IS USABLE
CREATE TABLE track_clean AS 
	SELECT track_id,
		track_name,
		energy,
		STRING_AGG(track_genre, ',') AS genre,
		CONCAT_WS(',', artist1, artist2, artist3,artist4)
	FROM tracks_raw
	GROUP BY track_id, track_name, energy, artist1, artist2, artist3, artist4;

ALTER TABLE track_clean
RENAME COLUMN concat_ws TO artists;

ALTER TABLE track_clean
ADD PRIMARY KEY (track_id);

SELECT *
FROM track_clean;

-- CREATE TEMP TABLE FOR SAVING PICKED TRACKS
CREATE TEMP TABLE picked_tracks (
	track_id VARCHAR PRIMARY KEY,
	energy NUMERIC,
	genre VARCHAR
);

-- CREATE DYNAMIC TABLE FOR THE PICKED SONGS
CREATE TEMP TABLE calc_track AS
	SELECT c.track_id,
		c.energy,
		c.genre
	FROM track_clean AS c
	INNER JOIN picked_tracks AS p
		ON c.track_id = p.track_id;

-- CTE FOR CALCULATION
WITH energy_cal AS (
	SELECT AVG(energy) AS avg,
		STDDEV(energy) AS std
	FROM calc_track
),
picked_genre AS (
	SELECT DISTINCT unnest(string_to_array(genre, ',')) AS genre
    FROM calc_track
)

-- SHOWS THE RECOMMENDED TRACKS
SELECT t.*
FROM track_clean t, energy_cal ec
WHERE t.energy BETWEEN (ec.avg- ec.std)
                  AND (ec.avg+ ec.std)
  AND EXISTS (
      SELECT 1 FROM picked_genre g
      WHERE t.genre ILIKE '%' || g.genre || '%'
  )
  AND t.track_id NOT IN (SELECT track_id FROM picked_tracks);
