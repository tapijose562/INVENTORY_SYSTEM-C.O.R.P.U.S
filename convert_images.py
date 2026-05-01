#!/usr/bin/env python
"""
Convertir imágenes AVIF a PNG real
"""

from PIL import Image
from pathlib import Path

print("🔄 Convirtiendo imágenes Adidas de AVIF a PNG...\n")

adidas_dir = Path("assets/images/adidas_runner")

for img_path in adidas_dir.glob("*.png"):
    try:
        print(f"Procesando: {img_path.name}")
        img = Image.open(img_path)
        
        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Guardar como PNG real
        img.save(str(img_path), 'PNG')
        print(f"   ✅ {img_path.name} convertido\n")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")

print("✅ Conversión completada")
