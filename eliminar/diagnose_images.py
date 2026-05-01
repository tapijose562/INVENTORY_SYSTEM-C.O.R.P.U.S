#!/usr/bin/env python3
"""
Diagnose script to verify product images are being saved and retrieved correctly
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.db.database import SessionLocal
from app.models.product import Product, ProductImage

def diagnose_images():
    """Diagnose image storage and retrieval"""
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("🔍 PRODUCT IMAGES DIAGNOSTIC REPORT")
    print("="*60 + "\n")
    
    # Check 1: Uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        image_files = list(Path(uploads_dir).glob("*.jpg")) + \
                      list(Path(uploads_dir).glob("*.png")) + \
                      list(Path(uploads_dir).glob("*.jpeg"))
        print(f"✅ Uploads directory exists: {os.path.abspath(uploads_dir)}")
        print(f"   Found {len(image_files)} image files")
        if image_files:
            print("   Sample files:")
            for img in image_files[:5]:
                size_kb = os.path.getsize(img) / 1024
                print(f"   - {img.name} ({size_kb:.1f} KB)")
    else:
        print(f"❌ Uploads directory NOT found: {uploads_dir}")
    
    # Check 2: Database ProductImage count
    try:
        product_count = db.query(Product).count()
        image_count = db.query(ProductImage).count()
        
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"   Total Products: {product_count}")
        print(f"   Total ProductImages: {image_count}")
        
        if product_count > 0:
            print(f"\n📋 PRODUCTS WITH IMAGES:")
            products = db.query(Product).all()
            for product in products:
                images = db.query(ProductImage).filter(
                    ProductImage.product_id == product.id
                ).all()
                
                if images:
                    print(f"\n   Product #{product.id}: {product.name}")
                    print(f"   Brand: {product.brand}")
                    print(f"   Images: {len(images)}")
                    for img in images:
                        exists = os.path.exists(img.image_url.lstrip('/')) if img.image_url.startswith('/') else False
                        status = "✅" if exists else "❌"
                        print(f"   {status} {img.image_filename}")
                        print(f"      URL: {img.image_url}")
                        print(f"      Status: {img.status}")
                        print(f"      Primary: {'Yes' if img.is_primary else 'No'}")
        
        # Check 3: Orphaned images (in DB but file not found)
        print(f"\n🔗 ORPHANED IMAGES CHECK:")
        orphaned = 0
        for img in db.query(ProductImage).all():
            # Check if file exists
            file_path = img.image_url.lstrip('/')
            if not os.path.exists(file_path):
                orphaned += 1
                if orphaned <= 5:  # Show first 5
                    print(f"   ❌ Missing file: {img.image_filename}")
                    print(f"      Expected path: {file_path}")
        
        if orphaned > 0:
            print(f"   Found {orphaned} orphaned image records (files not found on disk)")
        else:
            print(f"   ✅ All images have corresponding files")
        
        # Check 4: Product image_url field
        print(f"\n🖼️  PRODUCT IMAGE_URL CHECK:")
        products_with_url = db.query(Product).filter(Product.image_url.isnot(None)).count()
        print(f"   Products with image_url: {products_with_url}/{product_count}")
        
        if products_with_url > 0:
            print(f"   Sample product URLs:")
            for product in db.query(Product).filter(Product.image_url.isnot(None)).limit(5):
                print(f"   - {product.name}: {product.image_url}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("📝 RECOMMENDATIONS:")
    print("="*60)
    print("""
1. Ensure Angular proxy includes both /api/* and /uploads/* routes
2. Check that images are being uploaded via the batch endpoint
3. Verify ProductImage records are created with correct URLs
4. Test image loading by opening URLs in browser: http://localhost:8000/uploads/...
5. Check browser Network tab for 404 errors on image requests
6. Verify CORS headers allow image requests from frontend

NEXT STEPS:
- Run backend: python backend/main.py
- Run frontend: npm start (ensure proxy.conf.json is configured)
- Create a test product with images in Detection component
- Check this diagnostic again
    """)

if __name__ == "__main__":
    diagnose_images()
