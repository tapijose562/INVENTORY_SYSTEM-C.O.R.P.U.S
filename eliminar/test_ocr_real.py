#!/usr/bin/env python3
"""
Script para probar OCR con imagen real
"""
import cv2
import numpy as np
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai import OCRService

def test_ocr_real_image():
    """Probar OCR con imagen real"""
    image_path = "../test_shoe_improved.jpg"

    if not os.path.exists(image_path):
        print(f"❌ Imagen no encontrada: {image_path}")
        return

    print(f"🧪 Probando OCR con imagen real: {image_path}")

    # Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Error cargando imagen")
        return

    print(f"📏 Imagen cargada: {img.shape}")

    # Probar OCR sin bbox
    print("\n🔍 Probando OCR en imagen completa...")
    result = OCRService.extract_text(img)
    print(f"Resultado: '{result}'")

    # Probar OCR con bbox típico para zapatos
    print("\n🔍 Probando OCR con bbox típico...")
    height, width = img.shape[:2]
    bbox = [int(width * 0.2), int(height * 0.15), int(width * 0.8), int(height * 0.45)]
    print(f"Usando bbox: {bbox}")
    result_bbox = OCRService.extract_text(img, bbox)
    print(f"Resultado con bbox: '{result_bbox}'")

    print("\n✅ Prueba con imagen real completada")

if __name__ == "__main__":
    test_ocr_real_image()