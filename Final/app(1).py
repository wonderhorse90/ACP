from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DB_CONFIG = {
    'host': 'zefanya21.mysql.pythonanywhere-services.com',
    'user': 'zefanya21',
    'password': 'mysqlroot',
    'database': 'zefanya21$acp_project'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    searched = None
    found_songs = []
    selected = session.get('selected_tracks', [])
    tracks = []

    if request.method == 'POST':
        searched = request.form.get('track_name')

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT track_id, track_name, energy, genre, artists
            FROM track_clean
            WHERE track_name LIKE %s
            LIMIT 10
        """, (f"%{searched}%",))
        found_songs = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template('second-page.html',
                           found_songs=found_songs,
                           searched=searched,
                           selected=selected,
                           tracks=tracks)

@app.route('/add_track_direct')
def add_track_direct():
    track_name = request.args.get('track_name')

    if 'selected_tracks' not in session:
        session['selected_tracks'] = []

    if track_name and track_name not in session['selected_tracks']:
        session['selected_tracks'].append(track_name)
        session.modified = True

    return redirect(url_for('recommendations'))

@app.route('/remove_track/<track_name>')
def remove_track(track_name):
    if 'selected_tracks' in session and track_name in session['selected_tracks']:
        session['selected_tracks'].remove(track_name)
        session.modified = True
    return redirect(url_for('recommendations'))

@app.route('/clear_tracks')
def clear_tracks():
    session['selected_tracks'] = []
    session.modified = True
    return redirect(url_for('recommendations'))


@app.route('/show_recommendations')
def show_recommendations():
    selected_tracks = session.get('selected_tracks', [])
    recommendations = []

    if selected_tracks:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Fetch energy and genre of each selected track
        format_strings = ','.join(['%s'] * len(selected_tracks))
        cursor.execute(f"""
            SELECT track_id, energy, genre
            FROM track_clean
            WHERE track_name IN ({format_strings})
        """, tuple(selected_tracks))
        selected_data = cursor.fetchall()

        if selected_data:
            energies = [row['energy'] for row in selected_data if row['energy'] is not None]
            genres = set(g.split(',')[0] for row in selected_data if row['genre'] for g in [row['genre']])

            if energies and genres:
                avg_energy = sum(energies) / len(energies)
                std_energy = (sum((e - avg_energy) ** 2 for e in energies) / len(energies)) ** 0.5

                # Prepare genre conditions
                genre_conditions = ' OR '.join(["genre LIKE %s" for _ in genres])
                genre_values = [f"%{g}%" for g in genres]

                # Final query
                cursor.execute(f"""
                    SELECT track_name, energy, genre, artists
                    FROM track_clean
                    WHERE energy BETWEEN %s AND %s
                      AND ({genre_conditions})
                      AND track_name NOT IN ({format_strings})
                    LIMIT 10
                """, (avg_energy - std_energy, avg_energy + std_energy, *genre_values, *selected_tracks))

                recommendations = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template('second-page.html',
                           found_songs=[],
                           searched=None,
                           selected=selected_tracks,
                           tracks=recommendations)
