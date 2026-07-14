import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "closet.db"

def get_connection():
    """Returns a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

def init_db():
    """Creates all tables if they don't already exist. Safe to call every app run."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clothing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            category TEXT NOT NULL,        -- shirt, pant, shoes, accessory
            sub_type TEXT,                 -- polo, formal shirt, jeans, etc.
            formality TEXT NOT NULL,       -- casual, business, formal
            dominant_color TEXT NOT NULL,  -- hex code, e.g. #1a2b3c (primary/largest color)
            color_name TEXT,               -- human readable, e.g. "navy blue"
            colors TEXT,                   -- JSON list of ALL detected colors (multi-color support)
            wear_count INTEGER DEFAULT 0,
            last_worn_date TEXT,           -- ISO date string
            is_dirty INTEGER DEFAULT 0,    -- 0 = clean, 1 = needs wash
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("PRAGMA table_info(clothing_items)")
    existing_columns = {row[1] for row in cur.fetchall()}
    if "colors" not in existing_columns:
        cur.execute("ALTER TABLE clothing_items ADD COLUMN colors TEXT")
    if "pattern" not in existing_columns:
        cur.execute("ALTER TABLE clothing_items ADD COLUMN pattern TEXT DEFAULT 'neutral'")
    if "season" not in existing_columns:
        cur.execute("ALTER TABLE clothing_items ADD COLUMN season TEXT DEFAULT 'all-season'")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS outfit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_ids TEXT NOT NULL,        -- comma-separated clothing_items.id
            context TEXT NOT NULL,         -- office, friend, university, trip
            worn_date TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reserved_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            start_date TEXT NOT NULL,      -- ISO date string
            end_date TEXT NOT NULL,
            reserved_item_ids TEXT NOT NULL  -- comma-separated clothing_items.id
        )
    """)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")