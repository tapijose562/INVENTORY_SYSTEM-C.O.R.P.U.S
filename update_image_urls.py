#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('backend/inventory.db')
cursor = conn.cursor()

print("=== UPDATING IMAGE URLs ===")

# Get all product images
cursor.execute("SELECT id, image_url FROM product_images")
images = cursor.fetchall()

updated_count = 0
for image_id, image_url in images:
    if image_url and image_url.startswith('/api/v1/product-images/file/'):
        # Extract filename from old URL
        filename = image_url.replace('/api/v1/product-images/file/', '')
        new_url = f'/uploads/{filename}'

        # Update the URL
        cursor.execute("UPDATE product_images SET image_url = ? WHERE id = ?", (new_url, image_id))
        print(f"Updated ID {image_id}: {image_url} -> {new_url}")
        updated_count += 1

# Also update product.image_url if it uses the old format
cursor.execute("SELECT id, image_url FROM products WHERE image_url LIKE '/api/v1/product-images/file/%'")
products = cursor.fetchall()

for product_id, image_url in products:
    if image_url and image_url.startswith('/api/v1/product-images/file/'):
        filename = image_url.replace('/api/v1/product-images/file/', '')
        new_url = f'/uploads/{filename}'

        cursor.execute("UPDATE products SET image_url = ? WHERE id = ?", (new_url, product_id))
        print(f"Updated Product ID {product_id}: {image_url} -> {new_url}")
        updated_count += 1

conn.commit()
conn.close()

print(f"\n✅ Updated {updated_count} image URLs to use /uploads/ format")