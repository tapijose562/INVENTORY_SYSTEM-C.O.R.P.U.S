#!/usr/bin/env python
"""
Color Detection Utility
Extracts dominant colors from shoe images
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict

class ShoeColorAnalyzer:
    """Analyzes shoe colors with high precision"""
    
    COLOR_NAMES = {
        "black": ([0, 0, 0], [50, 50, 50]),
        "white": ([200, 200, 200], [255, 255, 255]),
        "red": ([0, 0, 100], [100, 50, 255]),
        "green": ([0, 100, 0], [100, 255, 100]),
        "blue": ([100, 0, 0], [255, 50, 100]),
        "yellow": ([0, 100, 100], [100, 200, 255]),
        "orange": ([0, 100, 150], [100, 200, 255]),
        "purple": ([100, 0, 100], [255, 100, 255]),
        "brown": ([0, 50, 100], [100, 150, 200]),
        "gray": ([50, 50, 50], [150, 150, 150]),
    }
    
    @staticmethod
    def extract_dominant_colors(image: np.ndarray, k: int = 3) -> list:
        """Extract top K dominant colors from image"""
        
        # Reshape image to 2D array
        pixels = image.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # Apply K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        
        # Count pixels for each cluster
        unique, counts = np.unique(labels, return_counts=True)
        
        # Sort by pixel count (descending)
        sorted_idx = np.argsort(-counts)
        
        colors = []
        for idx in sorted_idx[:k]:
            color = [int(c) for c in centers[idx]]
            percentage = (counts[idx] / len(pixels)) * 100
            colors.append({
                "rgb": {"r": color[2], "g": color[1], "b": color[0]},
                "bgr": color,
                "percentage": percentage,
                "name": ShoeColorAnalyzer._get_color_name(color)
            })
        
        return colors
    
    @staticmethod
    def _get_color_name(bgr: list) -> str:
        """Get color name from BGR values"""
        min_distance = float('inf')
        closest_color = "other"
        
        for color_name, (lower, upper) in ShoeColorAnalyzer.COLOR_NAMES.items():
            distance = sum([(bgr[i] - (lower[i] + upper[i]) / 2) ** 2 for i in range(3)])
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        return closest_color
    
    @staticmethod
    def analyze_shoe_image(image_path: str, bbox: Tuple[int, int, int, int] = None) -> Dict:
        """Analyze shoe image and extract color information"""
        
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Cannot load image"}
        
        # Extract ROI if bbox provided
        if bbox:
            x1, y1, x2, y2 = bbox
            roi = image[y1:y2, x1:x2]
        else:
            roi = image
        
        # Extract dominant colors
        colors = ShoeColorAnalyzer.extract_dominant_colors(roi, k=3)
        
        return {
            "primary_color": colors[0] if colors else None,
            "secondary_color": colors[1] if len(colors) > 1 else None,
            "tertiary_color": colors[2] if len(colors) > 2 else None,
            "all_colors": colors
        }

if __name__ == "__main__":
    # Example usage
    analyzer = ShoeColorAnalyzer()
    # result = analyzer.analyze_shoe_image("path/to/shoe.jpg")
    # print(result)
