#!/usr/bin/env python3
"""Test script to verify batch image upload endpoint works correctly"""

import os
import sys
import requests
from pathlib import Path
import tempfile

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

def create_test_image():
    """Create a simple test image file"""
    import cv2
    import numpy as np

    # Create a simple 100x100 red image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [255, 0, 0]  # Red color

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    cv2.imwrite(temp_file.name, img)
    return temp_file.name

def test_batch_upload():
    """Test the batch upload endpoint"""
    print("🔍 Testing Batch Image Upload Endpoint")

    # Login first
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if login_response.status_code != 200:
            print(f"  ❌ Login failed: {login_response.status_code}")
            print(f"     {login_response.text}")
            return False

        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"  ✅ Logged in successfully")

    except Exception as e:
        print(f"  ❌ Login error: {e}")
        return False

    # Create a test product
    try:
        product_response = requests.post(
            "http://localhost:8000/api/v1/products/",
            json={
                "name": "Test Batch Upload Product",
                "brand": "TestBrand",
                "size": "10",
                "stock": 5,
                "yolo_confidence": 0.85
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if product_response.status_code != 200:
            print(f"  ❌ Product creation failed: {product_response.status_code}")
            print(f"     {product_response.text}")
            return False

        product = product_response.json()
        product_id = product.get("id")
        print(f"  ✅ Created test product with ID: {product_id}")

    except Exception as e:
        print(f"  ❌ Product creation error: {e}")
        return False

    # Create test images
    test_images = []
    try:
        for i in range(4):  # Create 4 test images (should be allowed)
            img_path = create_test_image()
            test_images.append(img_path)
            print(f"  ✅ Created test image: {img_path}")

        # Upload batch images
        files = []
        for i, img_path in enumerate(test_images):
            files.append(('files', (f'test_image_{i+1}.png', open(img_path, 'rb'), 'image/png')))

        upload_response = requests.post(
            f"http://localhost:8000/api/v1/product-images/upload-batch",
            data={'product_id': str(product_id)},
            files=files,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        # Close file handles
        for _, file_tuple in files:
            file_tuple[1].close()

        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"  ✅ Batch upload successful!")
            print(f"     Uploaded {result.get('total_images', 0)} images")
            print(f"     Max images allowed: {result.get('max_images', 0)}")
            return True
        else:
            print(f"  ❌ Batch upload failed: {upload_response.status_code}")
            print(f"     {upload_response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Upload error: {e}")
        return False
    finally:
        # Clean up test images
        for img_path in test_images:
            try:
                os.unlink(img_path)
            except:
                pass

def main():
    """Run the batch upload test"""
    print("=" * 60)
    print("Batch Image Upload Test")
    print("=" * 60)

    success = test_batch_upload()

    print("\n" + "=" * 60)
    if success:
        print("✅ Batch upload test PASSED!")
        print("The batch upload endpoint is working correctly.")
    else:
        print("❌ Batch upload test FAILED!")
        print("Check the backend logs for more details.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())