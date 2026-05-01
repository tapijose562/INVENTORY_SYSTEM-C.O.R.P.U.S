#!/usr/bin/env python3
"""Test database creation"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.db.database import Base, engine
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
except Exception as e:
    print(f"❌ Error creating database: {e}")
    import traceback
    traceback.print_exc()