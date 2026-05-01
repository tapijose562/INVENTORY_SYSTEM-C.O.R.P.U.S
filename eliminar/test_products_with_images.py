#!/usr/bin/env python3
import requests
import json

# Test the products endpoint
try:
    response = requests.get("http://localhost:8000/api/v1/products/")
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products")
        for i, product in enumerate(products[:3]):  # Show first 3
            print(f"\n📦 Product {i+1}: {product['name']} ({product['brand']})")
            print(f"   Image URL: {product.get('image_url', 'None')}")
            images = product.get('images', [])
            print(f"   Images count: {len(images)}")
            if images:
                for j, img in enumerate(images[:2]):  # Show first 2 images
                    print(f"     Image {j+1}: {img['url']} (primary: {img['is_primary']})")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Failed to connect: {e}")