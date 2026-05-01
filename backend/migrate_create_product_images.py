#!/usr/bin/env python
"""Migration script to create product_images table"""
import sqlite3
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

def migrate_create_product_images_table():
    """Create product_images table"""
    
    # Get database path
    db_path = settings.database_url.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='product_images'
        """)
        
        if cursor.fetchone():
            print("✅ Table 'product_images' already exists")
            conn.close()
            return True
        
        # Create table
        print("📝 Creating 'product_images' table...")
        cursor.execute("""
            CREATE TABLE product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                detection_log_id INTEGER,
                image_url VARCHAR(500) NOT NULL,
                image_filename VARCHAR(200) NOT NULL,
                image_size INTEGER,
                detected_brand VARCHAR(100),
                detected_color VARCHAR(50),
                detected_size VARCHAR(20),
                detected_text TEXT,
                confidence_score REAL,
                price REAL,
                selection_data TEXT,
                detection_metadata TEXT,
                image_metadata TEXT,
                is_primary INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (detection_log_id) REFERENCES detection_logs(id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX idx_product_images_product_id 
            ON product_images(product_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_product_images_image_url 
            ON product_images(image_url)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("✅ Table 'product_images' created with all columns")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_create_product_images_table()
    sys.exit(0 if success else 1)
