#!/usr/bin/env python3
import sqlite3
import os

# Connect to database
conn = sqlite3.connect('backend/inventory.db')
cursor = conn.cursor()

print("=== PRODUCT IMAGES IN DATABASE ===")
cursor.execute("SELECT id, product_id, image_url, image_filename, is_primary FROM product_images ORDER BY product_id, id")
images = cursor.fetchall()
for image in images:
    print(f"ID: {image[0]}, Product: {image[1]}, URL: {image[2]}, Filename: {image[3]}, Primary: {image[4]}")

print("\n=== PRODUCTS ===")
cursor.execute("SELECT id, name, image_url FROM products LIMIT 10")
products = cursor.fetchall()
for product in products:
    print(f"ID: {product[0]}, Name: {product[1]}, Image URL: {product[2]}")

print("\n=== FILES IN UPLOADS DIRECTORY ===")
uploads_dir = 'backend/uploads'
if os.path.exists(uploads_dir):
    files = os.listdir(uploads_dir)
    print(f"Found {len(files)} files:")
    for file in files[:10]:  # Show first 10
        print(f"  {file}")
else:
    print("Uploads directory does not exist!")

conn.close()