#!/usr/bin/env python3
"""
Test script for Corpus Detector Integration
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_corpus_detector_status():
    """Test corpus detector status endpoint"""
    print("🔍 Probando status del detector Corpus...")

    try:
        response = requests.get("http://localhost:8000/api/detection/corpus-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data}")
            return data.get('available', False)
        else:
            print(f"❌ Error en status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

def test_corpus_detection():
    """Test corpus detection with sample image"""
    print("🖼️ Probando detección con modelo Corpus...")

    # Find a test image
    test_images = [
        "backend/uploads/detect_*.jpg",
        "backend/test_images/*.jpg",
        "assets/images/*/*.jpg"
    ]

    test_image_path = None
    for pattern in test_images:
        import glob
        matches = glob.glob(pattern)
        if matches:
            test_image_path = matches[0]
            break

    if not test_image_path:
        print("⚠️ No se encontró imagen de prueba, creando una imagen dummy...")
        import cv2
        import numpy as np

        # Create a dummy image with a rectangle (simulating a shoe)
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:] = [200, 200, 200]  # Light gray background

        # Draw a rectangle (simulating a shoe)
        cv2.rectangle(img, (150, 150), (450, 350), (0, 0, 255), 3)

        # Add some text
        cv2.putText(img, "NIKE", (200, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        test_image_path = "backend/test_shoe.jpg"
        cv2.imwrite(test_image_path, img)
        print(f"📝 Imagen dummy creada: {test_image_path}")

    if not os.path.exists(test_image_path):
        print(f"❌ Imagen de prueba no encontrada: {test_image_path}")
        return False

    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            response = requests.post("http://localhost:8000/api/detection/detect-corpus", files=files)

        if response.status_code == 200:
            result = response.json()
            print("✅ Detección exitosa:")
            print(f"   Marca: {result.get('brand', 'N/A')}")
            print(f"   Confianza: {result.get('confidence', 0):.2f}")
            print(f"   Color: {result.get('color', 'N/A')}")
            print(f"   Texto: {result.get('text', 'N/A')}")
            return True
        else:
            print(f"❌ Error en detección: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def test_realtime_detection():
    """Test real-time detection endpoint"""
    print("⚡ Probando detección en tiempo real...")

    # Use the same test image
    test_image_path = "backend/test_shoe.jpg"
    if not os.path.exists(test_image_path):
        print("⚠️ Creando imagen de prueba para tiempo real...")
        import cv2
        import numpy as np

        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:] = [255, 255, 255]
        cv2.rectangle(img, (100, 100), (500, 300), (255, 0, 0), 2)
        cv2.putText(img, "SHOE", (200, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imwrite(test_image_path, img)

    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('frame.jpg', f, 'image/jpeg')}
            response = requests.post("http://localhost:8000/api/detection/detect-corpus-realtime", files=files)

        if response.status_code == 200:
            result = response.json()
            detections = result.get('detections', [])
            summary = result.get('summary', {})

            print("✅ Detección en tiempo real exitosa:")
            print(f"   Detecciones: {len(detections)}")
            print(f"   Resumen: {summary}")
            return True
        else:
            print(f"❌ Error en tiempo real: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error en tiempo real: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Iniciando pruebas de integración Corpus Detector")
    print("=" * 60)

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Backend no está ejecutándose en http://localhost:8000")
            print("💡 Ejecuta: cd backend && python main.py")
            return
    except:
        print("❌ No se puede conectar al backend")
        print("💡 Ejecuta: cd backend && python main.py")
        return

    print("✅ Backend detectado")

    # Test status
    if not test_corpus_detector_status():
        print("❌ Detector Corpus no disponible")
        return

    print()

    # Test detection
    if not test_corpus_detection():
        print("❌ Falló detección con modelo Corpus")
        return

    print()

    # Test real-time
    if not test_realtime_detection():
        print("❌ Falló detección en tiempo real")
        return

    print()
    print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("📱 El modelo Corpus está integrado y funcionando")
    print()
    print("💡 Usos principales:")
    print("   • Detección de zapatos con IA entrenada")
    print("   • Análisis de marca, color y texto")
    print("   • Detección en tiempo real con webcam")
    print("   • Integración completa con el sistema de inventario")

if __name__ == "__main__":
    main()