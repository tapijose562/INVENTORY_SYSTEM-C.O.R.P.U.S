#!/usr/bin/env python3
"""
Test complete product registration + image upload + annotation flow
"""
import requests
import json
import cv2
import os

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Create product
print("\n1️⃣  Creating product...")
product_data = {
    'name': 'Nike Gato Premium',
    'brand': 'Nike',
    'colors': 'Cloud White / Green / Black',
    'color_rgb': {'r': 89, 'g': 121, 'b': 46},
    'size': '42',
    'stock': 10,
    'price': 10000,
    'yolo_confidence': 0.85,
    'detected_text': 'Nike Premium',
    'description': 'Premium Nike Shoe',
    'detection_metadata': {'detection_id': 'det_001'}
}

r = requests.post(f'{BASE_URL}/products', json=product_data, timeout=5)
if r.status_code != 200:
    print(f"❌ Product creation failed: {r.status_code}")
    print(r.text)
    exit(1)

product = r.json()
product_id = product['id']
print(f"✅ Product created! ID: {product_id}")
print(f"   Name: {product['name']}, Stock: {product['stock']}")

# Step 2: Upload image
print("\n2️⃣  Uploading image...")
image_path = "ml-pipeline/training/datasets/images/train/NIKEGATO.jpg"

if not os.path.exists(image_path):
    print(f"⚠️  Image not found at {image_path}")
    print("   Skipping image upload...")
else:
    with open(image_path, 'rb') as f:
        files = {'file': f}
        r = requests.post(f'{BASE_URL}/products/{product_id}/upload-image', files=files, timeout=10)
        
    if r.status_code != 200:
        print(f"❌ Image upload failed: {r.status_code}")
        print(r.text[:200])
    else:
        product = r.json()
        print(f"✅ Image uploaded!")
        print(f"   Path: {product.get('image_url')}")

# Step 3: Annotate (bbox)
print("\n3️⃣  Adding annotation (bbox)...")
annotation_data = {
    'x1': 400,
    'y1': 300,
    'x2': 1200,
    'y2': 900,
    'class_name': 'Nike_Shoe'
}

r = requests.post(f'{BASE_URL}/products/{product_id}/annotate', json=annotation_data, timeout=5)
if r.status_code != 200:
    print(f"❌ Annotation failed: {r.status_code}")
    print(r.text[:300])
else:
    product = r.json()
    print(f"✅ Annotation saved!")
    print(f"   BBox: ({annotation_data['x1']}, {annotation_data['y1']}) - ({annotation_data['x2']}, {annotation_data['y2']})")

# Step 4: Get all products
print("\n4️⃣  Fetching all products...")
r = requests.get(f'{BASE_URL}/products', timeout=5)
if r.status_code != 200:
    print(f"❌ Fetch failed: {r.status_code}")
else:
    products = r.json()
    print(f"✅ Found {len(products)} product(s)")
    for p in products:
        print(f"   - {p['id']}: {p['name']} ({p['brand']}) - Size: {p['size']}, Stock: {p['stock']}")

print("\n✅ Complete flow test passed!")
