#!/usr/bin/env python3
"""
Test script para verificar que el endpoint de corpus detection funciona
"""

import requests
import os
from pathlib import Path

# URL del endpoint
API_URL = "http://localhost:8000/api/v1/detection"

def test_corpus_status():
    """Probar que el corpus detector está disponible"""
    print("\n=== Testing Corpus Status ===")
    response = requests.get(f"{API_URL}/corpus-status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_detect_corpus(image_path: str):
    """Probar la detección con corpus detector"""
    print(f"\n=== Testing Corpus Detection with {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
        response = requests.post(f"{API_URL}/detect-corpus", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Detection successful!")
        print(f"   Brand: {data.get('brand')}")
        print(f"   Color: {data.get('color')}")
        print(f"   Size: {data.get('size')}")
        print(f"   Confidence: {data.get('confidence')}")
        print(f"   RGB: {data.get('rgb')}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Corpus Detection Endpoint")
    
    # Test status
    status = test_corpus_status()
    
    if not status.get("available"):
        print("⚠️ Corpus detector is not available!")
        exit(1)
    
    print("\n✅ Corpus detector is available!")
    
    # Find a test image
    test_images = [
        "backend/assets/images/product_1_e075b1cdaf704da9a13297b63597707d.jpg",
        "backend/assets/images/product_2_0ffdedb70d824a5ebce8a1bdd29dd81a.jpg",
        "backend/uploads/detect_*.jpg",
    ]
    
    # Use a simple test image or create one
    test_image_path = None
    for img in test_images:
        if "*" in img:
            matches = list(Path(".").glob(img))
            if matches:
                test_image_path = str(matches[0])
                break
        elif os.path.exists(img):
            test_image_path = img
            break
    
    if test_image_path:
        print(f"\nFound test image: {test_image_path}")
        result = test_detect_corpus(test_image_path)
        if result:
            print("\n✅ Corpus Detection Test PASSED!")
        else:
            print("\n❌ Corpus Detection Test FAILED!")
    else:
        print("\n⚠️ No test images found. Skipping detection test.")
        print("Please upload an image first through the web interface.")
