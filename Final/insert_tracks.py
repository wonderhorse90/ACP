import pandas as pd
import mysql.connector

# --- SETUP ---
username = 'zefanya21'
password = 'mysqlroot'
dbname = f'{username}$acp_project'
host = f'{username}.mysql.pythonanywhere-services.com'

# --- Read the CSV (tab-separated) ---
csv_path = f'/home/{username}/databases/clean2_data.csv'
df = pd.read_csv(csv_path, sep=',')

expected_cols = ['track_id','track_name', 'energy', 'track_genre', 'artist1', 'artist2', 'artist3', 'artist4']
for col in expected_cols:
    if col not in df.columns:
        df[col] = None
df = df[expected_cols]
df = df.where(pd.notnull(df), None)
#df = df.dropna()

# --- Connect to MySQL ---
conn = mysql.connector.connect(
    host=host,
    user=username,
    password=password,
    database=dbname
)
cursor = conn.cursor()

# --- Create tracks_raw table ---
with open(f'/home/{username}/databases/track_schema.sql', 'r') as f:
    schema_sql = f.read()
cursor.execute(schema_sql, multi=True)

# --- Insert CSV data ---
insert_query = """
REPLACE INTO tracks_raw
(track_id, track_name, energy, track_genre, artist1, artist2, artist3, artist4)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
for row in df.values.tolist():
    cursor.execute(insert_query, row)
conn.commit()

# --- Optional: Clean genre values ---
cursor.execute("""
UPDATE tracks_raw
SET track_genre = 'singer'
WHERE track_genre = 'singer-songwriter'
""")

# --- Create cleaned track table ---
cursor.execute("DROP TABLE IF EXISTS track_clean")
cursor.execute("""
CREATE TABLE track_clean AS
SELECT
    track_id,
    track_name,
    energy,
    GROUP_CONCAT(DISTINCT track_genre SEPARATOR ',') AS genre,
    CONCAT_WS(',', artist1, artist2, artist3, artist4) AS artists
FROM tracks_raw
GROUP BY track_id, track_name, energy, artist1, artist2, artist3, artist4;
""")
cursor.execute("ALTER TABLE track_clean ADD PRIMARY KEY (track_id);")

cursor.close()
conn.close()

print("✅ Data inserted and cleaned successfully.")
