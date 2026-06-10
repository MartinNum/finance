from app.database import engine, SessionLocal
from app.models import Base, Park, User
from app.auth import hash_password
from app.services.seed import create_park_seed_data

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create admin user
if not db.query(User).filter(User.username == "admin").first():
    db.add(User(
        username="admin",
        hashed_password=hash_password("Mdc15958497370"),
        display_name="管理员",
        role="admin",
    ))
    db.flush()

# Create default park with seed data
park = db.query(Park).filter(Park.name == "新华园区").first()
if not park:
    park = Park(name="新华园区")
    db.add(park)
    db.flush()
    create_park_seed_data(db, park.id)

# Create default park user
if not db.query(User).filter(User.username == "maxinghua").first():
    db.add(User(
        username="maxinghua",
        hashed_password=hash_password("mxh123456"),
        display_name="马兴华",
        role="user",
        park_id=park.id,
    ))

db.commit()
db.close()

print("Database initialized with seed data successfully!")
print("  Admin: admin / Mdc15958497370")
print("  Park:  新华园区")
print("  User:  maxinghua / mxh123456 -> 新华园区")
