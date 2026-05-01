#!/usr/bin/env python
"""Migration script to add missing columns to products table"""
import sqlite3
import os
import sys

# Add backend root to path if needed
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

REQUIRED_COLUMNS = {
    "colors": "TEXT",
    "color_primary": "TEXT",
    "color_secondary": "TEXT",
    "color_rgb": "TEXT",
    "detection_metadata": "TEXT",
    "image_url": "TEXT",
    "created_by": "INTEGER",
}


def migrate_add_product_columns():
    """Add missing product columns to the products table."""
    db_path = settings.database_url.replace("sqlite:///", "")

    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        if not columns:
            print("⚠️ Table 'products' does not exist yet. No migration needed.")
            conn.close()
            return True

        existing_names = {col[1] for col in columns}
        added = []

        for name, column_type in REQUIRED_COLUMNS.items():
            if name not in existing_names:
                print(f"📝 Adding missing column '{name}' to products table...")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {name} {column_type}")
                added.append(name)

        if added:
            conn.commit()
            print(f"✅ Migration completed. Added columns: {', '.join(added)}")
        else:
            print("✅ No missing columns found in products table.")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = migrate_add_product_columns()
    sys.exit(0 if success else 1)
