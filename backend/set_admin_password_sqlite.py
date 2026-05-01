import sqlite3
from app.core.security import hash_password

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()
try:
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    row = cur.fetchone()
    if not row:
        print('Admin user not found')
    else:
        new_hash = hash_password('admin123')
        cur.execute("UPDATE users SET hashed_password = ? WHERE username = 'admin'", (new_hash,))
        conn.commit()
        print('Admin password updated (hashed)')
finally:
    conn.close()
