import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        direction TEXT,
        from_addr TEXT,
        to_addr TEXT,
        subject TEXT,
        body TEXT,
        sent_at TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        event_type TEXT,
        url TEXT,
        timestamp TEXT
    )
    ''')
    conn.commit()

def get_cursor():
    return cursor

def get_conn():
    return conn