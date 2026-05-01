#!/usr/bin/env python3
"""
Script para probar OCR con imagen mejorada - debug detallado
"""
import cv2
import numpy as np
from pathlib import Path
import requests

# Crear imagen de prueba MEJORADA con texto grande y nítido
def create_better_test_image():
    print("📸 Creando imagen de prueba MEJORADA...")
    
    # Imagen más grande para mejor OCR
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Dibujar caja de zapato (marrón)
    cv2.rectangle(img, (50, 100), (750, 450), (70, 120, 180), -1)  # Relleno
    cv2.rectangle(img, (50, 100), (750, 450), (0, 0, 0), 4)         # Borde grueso
    
    # Añadir texto GRANDE y NÍTIDO
    cv2.putText(img, "NIKE AIR MAX", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)
    cv2.putText(img, "SIZE 42 EU", (100, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
    cv2.putText(img, "Black Color", (100, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3)
    
    # Suela del zapato
    cv2.rectangle(img, (80, 430), (720, 480), (100, 100, 100), -1)
    
    # Guardar
    p = Path("test_shoe_improved.jpg")
    cv2.imwrite(str(p), img)
    print(f"✅ Imagen creada: {p}")
    
    return p

def test_ocr_directly():
    """Prueba OCR directamente con pytesseract"""
    print("\n🔍 Probando OCR directamente con Tesseract...")
    
    try:
        import pytesseract
        from PIL import Image
        
        img = cv2.imread("test_shoe_improved.jpg")
        if img is None:
            print("❌ No se puede leer la imagen")
            return
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Intentar OCR
        text = pytesseract.image_to_string(thresh, lang='eng')
        
        print(f"✅ OCR Result: '{text}'")
        
        if not text.strip():
            print("⚠️  No se detectó texto. Probando con más procesamiento...")
            
            # Upscale
            upscale = cv2.resize(thresh, None, fx=2, fy=2)
            text = pytesseract.image_to_string(upscale, lang='eng')
            print(f"✅ OCR con upscale: '{text}'")
        
        return text
        
    except ImportError:
        print("❌ pytesseract no instalado")
    except Exception as e:
        print(f"❌ Error OCR: {e}")

def test_via_api():
    """Prueba a través de la API"""
    print("\n📡 Probando a través de API del backend...")
    
    try:
        with open("test_shoe_improved.jpg", "rb") as f:
            files = {'file': f}
            response = requests.post("http://localhost:8000/api/v1/detection/detect-from-image", files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}")
            return
        
        result = response.json()
        print("✅ Resultado API:")
        print(f"  Brand: {result.get('brand')}")
        print(f"  Color: {result.get('color')}")
        print(f"  Size: {result.get('size')}")
        print(f"  Text OCR: '{result.get('text')}'")
        print(f"  Confidence: {result.get('confidence'):.2%}")
        
        if not result.get('text'):
            print("⚠️  OCR vacío en la API también")
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend no está corriendo")
    except Exception as e:
        print(f"❌ Error API: {e}")

def main():
    print("=" * 70)
    print("🧪 DEBUG OCR - PRUEBA MEJORADA")
    print("=" * 70)
    
    # Crear imagen mejorada
    create_better_test_image()
    
    # Probar OCR directo
    test_ocr_directly()
    
    # Probar vía API
    test_via_api()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
