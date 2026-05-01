#!/usr/bin/env python3
"""
Script de prueba para reconocimiento de zapatos/elementos con detección completa
"""
import requests
import cv2
import numpy as np
from pathlib import Path
import json

# URLs del API
BACKEND_URL = "http://localhost:8000/api/v1"
DETECTION_ENDPOINT = f"{BACKEND_URL}/detection/detect-from-image"
SUGGEST_ENDPOINT = f"{BACKEND_URL}/detection/suggest-text"

def create_test_shoe_image():
    """Crea una imagen de prueba con texto que simula un zapato"""
    print("📸 Creando imagen de prueba...")
    
    # Crear imagen blanca
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # Dibujar un rectángulo que simula un zapato (color rojo/café)
    cv2.rectangle(img, (100, 100), (500, 300), (0, 100, 200), -1)  # Fondo zapato (café)
    cv2.rectangle(img, (100, 100), (500, 300), (0, 0, 0), 3)       # Borde
    
    # Añadir texto OCR simulado
    cv2.putText(img, "NIKE AIR", (150, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    cv2.putText(img, "SIZE 42", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # Añadir líneas decorativas (simular detalles de zapato)
    cv2.line(img, (120, 200), (480, 200), (0, 0, 0), 2)
    cv2.circle(img, (300, 320), 30, (100, 150, 200), -1)  # Simular suela
    
    # Guardar imagen
    test_image_path = Path("test_shoe.jpg")
    cv2.imwrite(str(test_image_path), img)
    print(f"✅ Imagen creada: {test_image_path}")
    
    return test_image_path

def test_detection(image_path):
    """Prueba la detección YOLO + Color + OCR"""
    print("\n🔍 Enviando imagen al backend para detección...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(DETECTION_ENDPOINT, files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
        
        result = response.json()
        print("✅ Detección completada:")
        print(f"  Brand: {result.get('brand')}")
        print(f"  Color: {result.get('color')}")
        print(f"  Size: {result.get('size')}")
        print(f"  Text: {result.get('text')}")
        print(f"  Confidence: {result.get('confidence'):.2%}")
        print(f"  RGB: R={result['rgb']['r']}, G={result['rgb']['g']}, B={result['rgb']['b']}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend en http://localhost:8000")
        print("   ¿Está corriendo? Ejecuta: python backend/main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_ai_suggestion(detection_result, image_path):
    """Prueba la sugerencia de IA"""
    print("\n🤖 Generando sugerencia de IA...")
    
    if not detection_result:
        print("❌ No hay resultado de detección")
        return
    
    try:
        ocr_text = detection_result.get('text', '')
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'ocr_text': ocr_text}
            response = requests.post(SUGGEST_ENDPOINT, files=files, data=data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            return
        
        result = response.json()
        suggestion = result.get('suggestion', '')
        
        print("✅ Sugerencia de IA generada:")
        print(f"  Original: '{ocr_text}'")
        print(f"  Sugerencia: '{suggestion}'")
        
        return suggestion
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 60)
    print("🧪 PRUEBA DE DETECCIÓN DE ZAPATOS/ELEMENTOS")
    print("=" * 60)
    
    # Crear imagen de prueba
    image_path = create_test_shoe_image()
    
    # Probar detección
    detection_result = test_detection(image_path)
    
    if detection_result:
        # Probar sugerencia IA
        test_ai_suggestion(detection_result, image_path)
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ PRUEBA FALLIDA")
        print("=" * 60)
    
    # Limpiar
    if Path("test_shoe.jpg").exists():
        Path("test_shoe.jpg").unlink()

if __name__ == "__main__":
    main()
