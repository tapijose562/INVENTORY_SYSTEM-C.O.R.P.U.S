#!/usr/bin/env python3
"""
Test script for the new detection endpoints
"""
import os
import sys
sys.path.append('.')

# Set environment to use SQLite
os.environ['DB_ENGINE'] = 'sqlite'

try:
    from app.core.config import settings
    print("✅ Config loaded successfully")
    print(f"DB_ENGINE: {settings.DB_ENGINE}")
    print(f"DATABASE_URL: {settings.database_url}")

    # Test imports
    from app.api.routes.detection import router
    print("✅ Detection routes imported successfully")

    from app.services.ai import YOLODetectionService
    print("✅ YOLO service imported successfully")

    print("\n🎉 All imports successful! The new endpoints should work.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()