#!/usr/bin/env python
"""Initialize database with default admin user"""
from app.core.security import hash_password
from app.db.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.role import Role


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

    # Create default roles and admin user if not exists
    db = SessionLocal()
    try:
        # Ensure roles
        for role_name, desc in [("admin", "Administrator"), ("client", "Cliente/Comprador")]:
            r = db.query(Role).filter(Role.name == role_name).first()
            if not r:
                r = Role(name=role_name, description=desc)
                db.add(r)
        db.commit()

        # Ensure admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("✅ Admin user already exists")
            return

        admin_user = User(
            username="admin",
            email="admin@inventory.local",
            full_name="Administrator",
            hashed_password=hash_password("admin123"),
            is_active=True,
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully (admin/admin123)")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
