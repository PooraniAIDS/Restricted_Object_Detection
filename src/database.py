import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.abspath("logs/restricted_objects.db")

def init_db():
    os.makedirs("logs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create detections table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            track_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL
        )
    ''')
    
    # Auto-migrate: Add is_restricted column if missing from earlier table schema
    cursor.execute("PRAGMA table_info(detections)")
    columns = [column[1] for column in cursor.fetchall()]
    if "is_restricted" not in columns:
        cursor.execute("ALTER TABLE detections ADD COLUMN is_restricted INTEGER DEFAULT 0")
        print("[INFO] Migrated database schema: Added 'is_restricted' column.")

    # Create restricted settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restricted_settings (
            category TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def set_restricted_categories(categories_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restricted_settings")
    for cat in categories_list:
        cursor.execute("INSERT OR REPLACE INTO restricted_settings (category) VALUES (?)", (cat.lower(),))
    conn.commit()
    conn.close()

def get_restricted_categories():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM restricted_settings")
    rows = cursor.fetchall()
    conn.close()
    return [r[0].lower() for r in rows]

def log_detection_to_db(track_id, category, confidence, is_restricted=0):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO detections (timestamp, track_id, category, confidence, is_restricted)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, track_id, category, round(confidence, 2), is_restricted))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"SQLite database successfully migrated at: {DB_PATH}")