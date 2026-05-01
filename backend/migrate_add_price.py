#!/usr/bin/env python
"""Migration script to add price column to detection_logs table"""
import sqlite3
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

def migrate_add_price_column():
    """Add price column to detection_logs table if it doesn't exist"""
    
    # Get database path
    db_path = settings.database_url.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(detection_logs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "price" in column_names:
            print("✅ Column 'price' already exists in detection_logs table")
            conn.close()
            return True
        
        # Add price column
        print("📝 Adding 'price' column to detection_logs table...")
        cursor.execute("""
            ALTER TABLE detection_logs 
            ADD COLUMN price REAL
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("✅ Column 'price' (REAL, nullable) added to detection_logs table")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_add_price_column()
    sys.exit(0 if success else 1)
