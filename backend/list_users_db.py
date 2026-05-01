import sqlite3
conn = sqlite3.connect('inventory.db')
cur = conn.cursor()
try:
    cur.execute('PRAGMA table_info(users)')
    print('users table columns:')
    for row in cur.fetchall():
        print(row)
    print('\nusers rows:')
    cur.execute('SELECT id, username, email, hashed_password, role, created_at FROM users')
    rows = cur.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
