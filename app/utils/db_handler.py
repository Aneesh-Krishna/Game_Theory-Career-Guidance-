# app/utils/db_handler.py

import sqlite3
import os
import json

# 🔧 Dynamically resolve absolute path to the data/ folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "sessions.db")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")

def init_db():
    """
    Ensure the data folder exists and initialize the SQLite DB.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            session_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_session(user_id, session_data):
    """
    Save session data to SQLite.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    json_data = json.dumps(session_data)
    cursor.execute('''
        INSERT OR REPLACE INTO sessions (user_id, session_data)
        VALUES (?, ?)
    ''', (user_id, json_data))
    conn.commit()
    conn.close()

def load_session(user_id):
    """
    Load session data from SQLite.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT session_data FROM sessions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def save_session_json(user_id, session_data):
    """
    Optional JSON backup.
    """
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
    with open(path, "w") as f:
        json.dump(session_data, f, indent=2)

def load_session_json(user_id):
    """
    Optional JSON restore.
    """
    path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)
