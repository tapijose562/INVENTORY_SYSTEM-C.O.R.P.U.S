#!/usr/bin/env python
"""Create admin user in database"""
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role

db = SessionLocal()

# Ensure admin role exists
admin_role = db.query(Role).filter(Role.name == 'admin').first()
if not admin_role:
    admin_role = Role(name='admin', description='Administrator role')
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# Check if admin already exists
existing = db.query(User).filter(User.username == 'admin').first()
if existing:
    print('✅ Admin user already exists')
    db.close()
    exit(0)

# Create admin user (change the password after first login)
hashed = hash_password('admin123')
user = User(
    username='admin',
    email='admin@inventory.local',
    full_name='Administrator',
    hashed_password=hashed,
    is_active=True,
    role='admin'
)

db.add(user)
db.commit()
print('✅ Admin user created successfully (username=admin)')
db.close()
