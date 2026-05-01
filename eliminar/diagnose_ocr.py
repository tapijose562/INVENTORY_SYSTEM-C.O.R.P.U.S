#!/usr/bin/env python3
"""
Diagnostic script for OCR troubleshooting
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def check_tesseract():
    """Check if Tesseract is installed"""
    print("\n" + "="*60)
    print("🔍 TESSERACT OCR DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Check configuration
    from app.core.config import settings
    print(f"📋 Configured Tesseract path:")
    print(f"   {settings.PYTESSERACT_PATH}\n")
    
    # Check if path exists
    if os.path.exists(settings.PYTESSERACT_PATH):
        print(f"✅ Tesseract ejecutable encontrado en:")
        print(f"   {settings.PYTESSERACT_PATH}")
    else:
        print(f"❌ Tesseract NO encontrado en:")
        print(f"   {settings.PYTESSERACT_PATH}\n")
        
        # Check common locations
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', 'User')),
        ]
        
        print("🔎 Buscando Tesseract en ubicaciones comunes:")
        found = False
        for path in common_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                print(f"   ✅ Encontrado en: {expanded_path}")
                found = True
            else:
                print(f"   ❌ No encontrado en: {expanded_path}")
        
        if not found:
            print("\n❌ Tesseract no está instalado en el sistema")
    
    # Check pytesseract module
    print("\n📦 Módulos OCR:")
    try:
        import pytesseract
        print(f"   ✅ pytesseract instalado (versión: {pytesseract.__version__ if hasattr(pytesseract, '__version__') else 'unknown'})")
    except ImportError:
        print(f"   ❌ pytesseract NO instalado")
    
    try:
        import easyocr
        print(f"   ✅ easyocr instalado")
    except ImportError:
        print(f"   ❌ easyocr NO instalado")
    
    # Test OCR service
    print("\n🧪 Testing OCRService:")
    try:
        from app.services.ai import OCRService
        print(f"   ✅ OCRService importado correctamente")
        
        # Create a test image
        import numpy as np
        import cv2
        
        # Create a simple test image with text
        test_img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Test OCR 123"
        cv2.putText(test_img, text, (50, 100), font, 1.5, (0, 0, 0), 2)
        
        print(f"   📝 Imagen de prueba creada: 200x400 con texto 'Test OCR 123'")
        
        # Try to extract text
        print(f"   ⏳ Extrayendo texto...")
        result = OCRService.extract_text(test_img)
        
        if result and len(result.strip()) > 0:
            print(f"   ✅ OCR funciona correctamente")
            print(f"   📖 Texto extraído: {result}")
        else:
            print(f"   ⚠️  OCR extrajo texto vacío")
            print(f"   💡 Posible causa: Tesseract no configurado, usando EasyOCR como fallback")
            
    except Exception as e:
        print(f"   ❌ Error en OCRService: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    print("\n" + "="*60)
    print("📝 SOLUCIONES:")
    print("="*60)
    print("""
1. Si Tesseract NO está instalado:
   
   a) Windows - Descargar: https://github.com/UB-Mannheim/tesseract/wiki
      - Installer: https://github.com/UB-Mannheim/tesseract/releases
      - Ejecutar el installer (mantener ruta por defecto)
      - Reiniciar el backend
   
   b) Linux (Ubuntu/Debian):
      sudo apt-get install tesseract-ocr
   
   c) MacOS:
      brew install tesseract

2. Si Tesseract está instalado pero en otra ubicación:
   
   Editar: backend/app/core/config.py
   
   Cambiar:
   PYTESSERACT_PATH: str = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
   
   Por tu ruta actual (ej):
   PYTESSERACT_PATH: str = r"C:/Users/{}/AppData/Local/Tesseract-OCR/tesseract.exe"

3. Si todo lo anterior falla:
   
   El sistema usa EasyOCR como fallback (ya está en requirements)
   - EasyOCR es más lento pero no requiere instalación adicional
   - Descargará modelos automáticamente en primera ejecución (~300MB)

4. Para verificar que funciona:
   
   cd backend
   python app/services/ai.py  # Para probar las funciones
   
   O testing manual:
   python -c "from app.services.ai import OCRService; import cv2; img = cv2.imread('test.jpg'); print(OCRService.extract_text(img))"
    """)
    
    print("\n" + "="*60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*60 + "\n")

if __name__ == "__main__":
    check_tesseract()
