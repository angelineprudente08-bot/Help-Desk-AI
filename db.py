import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATABASE = HERE / "helpdesk.db"   # the whole database lives in this one file, next to the code

def get_db():
    """Open a connection to the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row             # lets us use row["title"] instead of row[1]
    conn.execute("PRAGMA foreign_keys = ON")   # make SQLite enforce the REFERENCES rules
    return conn

def init_db():
    """Create all tables from schema.sql."""
    conn = get_db()
    with open(HERE / "schema.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def migrate_db():
    """Add tables that newer versions need. Safe to run on an existing database: nothing is deleted."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
          id INTEGER PRIMARY KEY,
          user_id INTEGER NOT NULL REFERENCES users(id),
          ticket_id INTEGER NOT NULL REFERENCES tickets(id),
          body TEXT NOT NULL,
          is_read INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
    # where a ticket's priority came from: model, rules, default (all automatic) or staff
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(tickets)")]
    if "priority_source" not in columns:
        conn.execute("ALTER TABLE tickets ADD COLUMN priority_source TEXT")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    conn = get_db()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("Tables created:", [t["name"] for t in tables])