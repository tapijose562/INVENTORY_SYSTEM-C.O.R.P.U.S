#!/usr/bin/env python3
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('backend/inventory.db')
cursor = conn.cursor()

# Check products
print("=== PRODUCTS ===")
cursor.execute("SELECT id, name, brand, image_url FROM products LIMIT 10")
products = cursor.fetchall()
for product in products:
    print(f"ID: {product[0]}, Name: {product[1]}, Brand: {product[2]}, Image URL: {product[3]}")

print("\n=== PRODUCT IMAGES ===")
cursor.execute("SELECT id, product_id, image_url, is_primary FROM product_images LIMIT 20")
images = cursor.fetchall()
for image in images:
    print(f"ID: {image[0]}, Product ID: {image[1]}, Image URL: {image[2]}, Is Primary: {image[3]}")

conn.close()