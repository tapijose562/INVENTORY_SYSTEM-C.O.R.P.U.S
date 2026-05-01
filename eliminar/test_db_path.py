#!/usr/bin/env python3
"""Test database path and connection"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

print(f"Database URL: {settings.database_url}")

# Extract the path from the URL
if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url[10:]  # Remove "sqlite:///"
    print(f"Database path: {db_path}")
    print(f"Path exists: {os.path.exists(db_path)}")
    print(f"Directory exists: {os.path.exists(os.path.dirname(db_path))}")
    print(f"Directory writable: {os.access(os.path.dirname(db_path), os.W_OK)}")

    # Try to connect
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()
        print("✅ SQLite connection successful")
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
else:
    print("Not a SQLite URL")