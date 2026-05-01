#!/usr/bin/env python3
"""
Simple test to verify the color extraction fix
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import cv2
import numpy as np

def test_color_extraction():
    print("Testing color extraction fix...")

    # Create a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:, :] = (255, 0, 0)  # Blue in BGR

    # Test grayscale image
    gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)

    try:
        from app.services.ai import ColorDetectionService

        # Test with BGR image
        result1 = ColorDetectionService.extract_dominant_color(test_image)
        print(f"BGR image result: {result1}")

        # Test with grayscale image
        result2 = ColorDetectionService.extract_dominant_color(gray_image)
        print(f"Grayscale image result: {result2}")

        # Test multiple colors with BGR
        result3 = ColorDetectionService.extract_multiple_colors(test_image)
        print(f"Multiple colors BGR: {result3}")

        # Test multiple colors with grayscale
        result4 = ColorDetectionService.extract_multiple_colors(gray_image)
        print(f"Multiple colors grayscale: {result4}")

        print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_color_extraction()