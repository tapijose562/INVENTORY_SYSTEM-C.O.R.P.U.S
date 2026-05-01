#!/usr/bin/env python
"""
OCR Text Detection Utility
Extracts text from shoe images (brand, size, model numbers)
"""

import pytesseract
import cv2
import numpy as np
import re
from typing import Dict, List

class ShoeOCRExtractor:
    """Extracts text information from shoe images"""
    
    def __init__(self, pytesseract_path: str = None):
        """Initialize OCR extractor"""
        if pytesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = pytesseract_path
    
    def extract_text(self, image: np.ndarray, bbox: tuple = None) -> str:
        """Extract text from image using Tesseract OCR"""
        
        # Extract ROI if bbox provided
        if bbox:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            roi = image[y1:y2, x1:x2]
        else:
            roi = image
        
        # Preprocess image
        preprocessed = self._preprocess_image(roi)
        
        # Extract text
        text = pytesseract.image_to_string(preprocessed)
        
        return text.strip()
    
    def extract_shoe_info(self, image: np.ndarray, bbox: tuple = None) -> Dict:
        """Extract shoe-specific information"""
        
        text = self.extract_text(image, bbox)
        
        # Extract different types of information
        info = {
            "raw_text": text,
            "size": self._extract_size(text),
            "numbers": self._extract_numbers(text),
            "model": self._extract_model(text),
            "brand_indicators": self._extract_brand_keywords(text)
        }
        
        return info
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Resize for better OCR (upscale)
        H, W = thresh.shape
        if W < 300:
            scale = 300 / W
            new_width = int(W * scale)
            new_height = int(H * scale)
            thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return thresh
    
    @staticmethod
    def _extract_numbers(text: str) -> List[str]:
        """Extract all numbers from text"""
        return re.findall(r'\d+', text)
    
    @staticmethod
    def _extract_size(text: str) -> List[str]:
        """Extract shoe sizes (typically single or double digit with possible .5)"""
        # US sizes typically range from 3.5 to 16
        sizes = re.findall(r'\d+\.?\d*', text)
        # Filter for reasonable shoe sizes
        shoe_sizes = [s for s in sizes if 3 <= float(s) <= 20]
        return shoe_sizes
    
    @staticmethod
    def _extract_model(text: str) -> str:
        """Extract model number/name"""
        # Look for patterns like: Model: XXXX or MODEL XXXX
        model_match = re.search(r'(?:model|mod|style)[\s:]*([A-Z0-9\-]+)', text, re.IGNORECASE)
        if model_match:
            return model_match.group(1)
        return None
    
    @staticmethod
    def _extract_brand_keywords(text: str) -> List[str]:
        """Extract brand-related keywords"""
        brands = ['nike', 'adidas', 'puma', 'reebok', 'new balance', 'jordan', 'converse']
        found_brands = []
        
        text_lower = text.lower()
        for brand in brands:
            if brand in text_lower:
                found_brands.append(brand)
        
        return found_brands

if __name__ == "__main__":
    # Example usage
    extractor = ShoeOCRExtractor()
    # text = extractor.extract_text(cv2.imread("shoe.jpg"))
    # print(text)
