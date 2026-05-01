#!/usr/bin/env python3
"""
Script de diagnóstico completo del sistema
"""
import sys
from pathlib import Path

print("=" * 70)
print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
print("=" * 70)

# 1. Verificar dependencias
print("\n1️⃣  Verificando dependencias instaladas...")
dependencies = {
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'pytesseract': 'Tesseract',
    'easyocr': 'EasyOCR',
    'PIL': 'Pillow',
    'torch': 'PyTorch (para EasyOCR)',
    'requests': 'Requests',
    'fastapi': 'FastAPI',
    'sqlalchemy': 'SQLAlchemy'
}

failed = []
for lib, name in dependencies.items():
    try:
        __import__(lib)
        print(f"  ✅ {name}")
    except ImportError as e:
        print(f"  ❌ {name}: {e}")
        failed.append((name, lib))

if failed:
    print(f"\n⚠️  Faltan {len(failed)} dependencias. Instalando...")
    import subprocess
    for name, lib in failed:
        print(f"  Instalando {name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", lib, "--quiet"])

# 2. Probar configuración
print("\n2️⃣  Verificando configuración...")
try:
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    from app.core.config import settings
    print(f"  ✅ Config DATABASE_URL: {settings.DATABASE_URL[:30]}...")
    print(f"  ✅ Config YOLO: {settings.YOLO_MODEL_PATH}")
    print(f"  ✅ Config Tesseract: {settings.PYTESSERACT_PATH}")
except Exception as e:
    print(f"  ❌ Error config: {e}")

# 3. Probar servicios
print("\n3️⃣  Probando servicios...")
try:
    from app.services.ai import YOLODetectionService, OCRService, ColorDetectionService, AISuggestionService
    print("  ✅ OCRService importado")
    print("  ✅ YOLODetectionService importado")
    print("  ✅ ColorDetectionService importado")
    print("  ✅ AISuggestionService importado")
except Exception as e:
    print(f"  ❌ Error importar servicios: {e}")
    sys.exit(1)

# 4. Probar YOLO
print("\n4️⃣  Inicializando YOLO...")
try:
    yolo_service = YOLODetectionService()
    if yolo_service.model:
        print(f"  ✅ YOLO model cargado: {type(yolo_service.model)}")
    else:
        print("  ❌ YOLO model no loaded")
except Exception as e:
    print(f"  ❌ Error YOLO: {e}")

# 5. Crear imagen de prueba y detectar
print("\n5️⃣  Probando detección con imagen de prueba...")
try:
    import cv2
    import numpy as np
    
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (100, 100), (500, 300), (0, 100, 200), -1)
    cv2.rectangle(img, (100, 100), (500, 300), (0, 0, 0), 3)
    cv2.putText(img, "NIKE TEST", (150, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    cv2.putText(img, "SIZE 42", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    detections = yolo_service.detect_shoes(img)
    print(f"  ✅ YOLO detections: {len(detections)} objeto(s)")
    if detections:
        det = detections[0]
        print(f"     - Class: {det.get('class')}")
        print(f"     - Confidence: {det.get('confidence'):.2%}")
        print(f"     - BBox: {det.get('bbox')}")
        
        # Probar color
        color_rgb, color_name = ColorDetectionService.extract_dominant_color(img, det.get('bbox'))
        print(f"  ✅ Color detectado: {color_name} (RGB: {color_rgb})")
        
        # Probar OCR
        print("  ⏳ Extrayendo OCR (puede tardar...)...")
        text = OCRService.extract_text(img, det.get('bbox'))
        if text:
            print(f"  ✅ OCR texto: '{text}'")
        else:
            print(f"  ⚠️  OCR no extrajo texto")
            
except Exception as e:
    print(f"  ❌ Error prueba detección: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 70)
