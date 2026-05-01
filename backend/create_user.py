#!/usr/bin/env python
"""Utility script to create a user in the backend database.

Usage examples:
  venv\Scripts\activate
  python create_user.py --username cliente --password cliente123 --role comprador
  python create_user.py --username admin2 --password AdminPass123 --role admin
"""
import argparse
import sys

from app.db.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def create_user(username: str, password: str, role: str = "comprador"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User '{username}' already exists (id={existing.id}, role={existing.role})")
            return False

        user = User(
            username=username,
            email=f"{username}@inventory.local",
            full_name=username.capitalize(),
            hashed_password=hash_password(password),
            is_active=True,
            role=role
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.username} (id={user.id}, role={user.role})")
        print(f"Credentials -> username: {username}  password: {password}")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Create a user in the Inventory Corpus v2 DB")
    parser.add_argument("--username", required=True, help="Username for the new user")
    parser.add_argument("--password", required=True, help="Password for the new user")
    parser.add_argument("--role", choices=["admin", "comprador", "user", "cliente"], default="comprador", help="Role for the user")

    args = parser.parse_args()

    ok = create_user(args.username, args.password, args.role)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
