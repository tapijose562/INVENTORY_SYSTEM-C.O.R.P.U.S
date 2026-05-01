#!/usr/bin/env python3
"""
Script para probar el OCR mejorado
"""
import cv2
import numpy as np
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai import OCRService

def test_ocr():
    """Probar OCR con una imagen de prueba"""
    print("🧪 Probando OCR mejorado...")

    # Crear una imagen de prueba simple con texto
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255  # Imagen blanca

    # Agregar texto usando OpenCV
    text = "NIKE AIR MAX"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 100), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

    print("📝 Imagen de prueba creada con texto: 'NIKE AIR MAX'")

    # Probar OCR sin bbox
    print("\n🔍 Probando OCR en imagen completa...")
    result = OCRService.extract_text(img)
    print(f"Resultado: '{result}'")

    # Probar OCR con bbox
    print("\n🔍 Probando OCR con bbox...")
    bbox = [40, 80, 350, 120]  # Alrededor del texto
    result_bbox = OCRService.extract_text(img, bbox)
    print(f"Resultado con bbox: '{result_bbox}'")

    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_ocr()