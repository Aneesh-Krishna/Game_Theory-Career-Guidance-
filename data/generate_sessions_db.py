# generate_sessions_db.py
import sqlite3
conn = sqlite3.connect("sessions.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    user_id TEXT PRIMARY KEY,
    session_data TEXT
)
''')
conn.commit()
conn.close()
