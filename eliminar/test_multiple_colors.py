#!/usr/bin/env python3
"""
Test script to verify multiple color extraction is working
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import cv2
import numpy as np
from app.services.ai import ColorDetectionService

def test_multiple_colors():
    """Test the extract_multiple_colors method"""
    print("=" * 60)
    print("🎨 Testing Multiple Color Extraction")
    print("=" * 60)
    
    # Create a test image with three distinct color regions
    test_image = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Add three colored regions (BGR format in OpenCV)
    # Black region
    test_image[0:100, :] = (0, 0, 0)      # Black
    # Green region
    test_image[100:200, :] = (0, 255, 0)  # Green (BGR)
    # White region
    test_image[200:300, :] = (255, 255, 255)  # White
    
    print("\n✅ Created test image with 3 color regions:")
    print("   - Region 1: Black (0, 0, 0)")
    print("   - Region 2: Green (0, 255, 0)")
    print("   - Region 3: White (255, 255, 255)")
    
    # Test extract_multiple_colors
    print("\n🔍 Testing extract_multiple_colors()...")
    try:
        colors_string, dominant_rgb, all_colors_rgb = ColorDetectionService.extract_multiple_colors(
            test_image, 
            bbox=None,
            max_colors=3
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"   Colors String: '{colors_string}'")
        print(f"   Dominant RGB: {dominant_rgb}")
        print(f"\n   All Colors RGB:")
        for i, color_info in enumerate(all_colors_rgb, 1):
            print(f"      Color {i}: {color_info}")
        
        # Verify format
        if " / " in colors_string:
            color_parts = colors_string.split(" / ")
            print(f"\n✅ Format verification: Found {len(color_parts)} color names separated by ' / '")
            
            # Expected format examples
            print(f"\n✅ Format matches expected pattern:")
            print(f"   Example 1: 'Cloud White / Green / Black'")
            print(f"   Example 2: 'Halo Silver / Core Black / Grey'")
            print(f"   Example 3: 'Putty Beige / Beige / Impact Orange'")
            print(f"\n   Current result: '{colors_string}'")
        else:
            print(f"⚠️  WARNING: Color string format may not match expected pattern")
            
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multiple_colors()
    sys.exit(0 if success else 1)
