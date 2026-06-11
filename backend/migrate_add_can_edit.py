"""Add can_edit column to users table."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "can_edit" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN can_edit BOOLEAN DEFAULT 1")
        conn.commit()
        print("Added can_edit column to users table (default=True)")
    else:
        print("can_edit column already exists")

    conn.close()


if __name__ == "__main__":
    migrate()
