from app.db.database import SessionLocal
from app.core.security import hash_password

DB = SessionLocal()
try:
    admin = DB.execute("SELECT id, username FROM users WHERE username='admin'").fetchone()
    if admin is None:
        print('Admin user not found')
    else:
        new_hash = hash_password('admin123')
        DB.execute("UPDATE users SET hashed_password=? WHERE username='admin'", (new_hash,))
        DB.commit()
        print('Admin password updated to admin123 (hashed)')
finally:
    DB.close()
