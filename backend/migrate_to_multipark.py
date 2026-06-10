"""
Migration script: adds Park/User tables and park_id to existing config tables.
Run once to migrate existing finance.db to multi-park schema.

Usage: cd backend && python migrate_to_multipark.py
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal
from app.models import Base, Park, User
from app.auth import hash_password
from app.services.seed import create_park_seed_data

DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Create new tables (parks, users) via SQLAlchemy
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 2. Create admin user
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            hashed_password=hash_password("Mdc15958497370"),
            display_name="管理员",
            role="admin",
            park_id=None,
        )
        db.add(admin)
        db.flush()
        print("Created admin user: admin")

    # 3. Create default park
    park = db.query(Park).filter(Park.name == "新华园区").first()
    if not park:
        park = Park(name="新华园区")
        db.add(park)
        db.flush()
        print(f"Created park: 新华园区 (id={park.id})")

    # 4. Create park user
    park_user = db.query(User).filter(User.username == "maxinghua").first()
    if not park_user:
        park_user = User(
            username="maxinghua",
            hashed_password=hash_password("mxh123456"),
            display_name="马兴华",
            role="user",
            park_id=park.id,
        )
        db.add(park_user)
        print("Created user: maxinghua -> 新华园区")

    db.commit()

    park_id = park.id

    # 5. Add park_id column to existing tables (if not already present)
    tables_to_update = ["cycles", "job_types", "expense_categories", "grape_grades"]

    for table in tables_to_update:
        columns = [row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        if "park_id" not in columns:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN park_id INTEGER REFERENCES parks(id)")
            cur.execute(f"UPDATE {table} SET park_id = ?", (park_id,))
            print(f"Added park_id to {table}, set existing rows to park_id={park_id}")
        else:
            cur.execute(f"UPDATE {table} SET park_id = ? WHERE park_id IS NULL", (park_id,))
            print(f"Table {table} already has park_id, updated NULLs")

    conn.commit()
    conn.close()
    db.close()

    print("\nMigration completed successfully!")
    print(f"  Admin: admin / Mdc15958497370")
    print(f"  Park:  新华园区")
    print(f"  User:  maxinghua / mxh123456 -> 新华园区")


if __name__ == "__main__":
    migrate()
