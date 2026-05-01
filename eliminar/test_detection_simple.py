#!/usr/bin/env python
"""
Script para probar la detección de zapatos
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.ai import YOLODetectionService, ColorDetectionService, OCRService

def test_detection():
    """Probar la detección con una imagen de prueba"""

    print("=== PRUEBA DE DETECCIÓN DE ZAPATOS ===\n")

    # Inicializar servicios
    print("1. Inicializando servicios...")
    yolo_service = YOLODetectionService()
    color_service = ColorDetectionService()
    ocr_service = OCRService()

    # Crear imagen de prueba simple (un rectángulo negro como "zapato")
    print("2. Creando imagen de prueba...")
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    # Dibujar un rectángulo blanco como objeto
    cv2.rectangle(image, (150, 150), (450, 350), (255, 255, 255), -1)
    # Agregar texto
    cv2.putText(image, "NIKE 42", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    print("3. Ejecutando detección YOLO...")
    detections = yolo_service.detect_shoes(image)
    print(f"   Detecciones encontradas: {len(detections)}")

    for i, det in enumerate(detections):
        print(f"   Detección {i+1}: {det}")

    if detections:
        best_detection = max(detections, key=lambda x: x["confidence"])
        bbox = best_detection["bbox"]

        print("4. Analizando color...")
        color_rgb, color_name = color_service.extract_dominant_color(image, bbox)
        print(f"   Color detectado: {color_name} (RGB: {color_rgb})")

        print("5. Ejecutando OCR...")
        detected_text = ocr_service.extract_text(image, bbox)
        print(f"   Texto detectado: '{detected_text}'")

        numbers = ocr_service.extract_numbers(detected_text)
        print(f"   Números encontrados: {numbers}")

    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_detection()