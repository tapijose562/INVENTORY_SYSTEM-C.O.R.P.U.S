#!/usr/bin/env python3
"""
Test OCR directamente en backend
"""
import sys
sys.path.insert(0, 'backend')

import cv2
import numpy as np
from app.services.ai import OCRService

print("=" * 80)
print("🔍 TEST OCR - DIAGNÓSTICO DIRECTO")
print("=" * 80)

# 1. Crear imagen de prueba con texto
print("\n1️⃣  Creando imagen con texto grande...")
img = np.ones((300, 500, 3), dtype=np.uint8) * 255

# Texto grande y claro
cv2.putText(img, "NIKE AIR MAX", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 3)
cv2.putText(img, "Size 42 EU", (50, 180), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "Black", (50, 250), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)

cv2.imwrite("test_ocr_simple.jpg", img)
print(f"   ✅ Imagen creada: test_ocr_simple.jpg ({img.shape})")

# 2. Test OCR sin bbox (full image)
print("\n2️⃣  Test OCR - Full image...")
text = OCRService.extract_text(img)
print(f"   📝 Texto extraído: '{text}'")
print(f"   Length: {len(text)} caracteres")

# 3. Test OCR con bbox (ROI)
print("\n3️⃣  Test OCR - Con ROI (bbox)...")
bbox = [20, 60, 480, 200]  # Área donde está el texto
text_roi = OCRService.extract_text(img, bbox)
print(f"   📝 Texto extraído (ROI): '{text_roi}'")
print(f"   Length: {len(text_roi)} caracteres")

# 4. Test extract_numbers
print("\n4️⃣  Test extract_numbers...")
if text:
    numbers = OCRService.extract_numbers(text)
    print(f"   🔢 Números encontrados: {numbers}")

# 5. Test con imagen más oscura (prueba de umbralización)
print("\n5️⃣  Test OCR - Imagen con fondo oscuro...")
img_dark = np.ones((300, 500, 3), dtype=np.uint8) * 50  # Fondo gris oscuro
cv2.putText(img_dark, "ADIDAS NMD", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 3)
cv2.putText(img_dark, "Size 40 EU", (50, 180), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)

text_dark = OCRService.extract_text(img_dark)
print(f"   📝 Texto extraído (dark): '{text_dark}'")

print("\n" + "=" * 80)
print("✅ TEST OCR COMPLETADO")
print("=" * 80)

# Resumen
print("\n📊 Resumen:")
print(f"   - Test 1 (Full): {'✅ OK' if len(text) > 0 else '❌ No se extrajeron caracteres'}")
print(f"   - Test 2 (ROI): {'✅ OK' if len(text_roi) > 0 else '❌ No se extrajeron caracteres'}")
print(f"   - Test 3 (Dark): {'✅ OK' if len(text_dark) > 0 else '❌ No se extrajeron caracteres'}")
