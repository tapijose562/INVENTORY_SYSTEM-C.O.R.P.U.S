#!/usr/bin/env python
"""
Script de setup para el Adidas Runner
Prepara las carpetas y crea los directorios necesarios
"""

from pathlib import Path
import os

def setup():
    print("\n" + "="*70)
    print("🔧 SETUP INICIAL - ADIDAS RUNNER")
    print("="*70 + "\n")
    
    # Crear estructura de directorios
    directories = [
        Path("assets/images/adidas_runner"),
        Path("data/raw/adidas_runner"),
        Path("data/processed/adidas_runner"),
        Path("data/annotations/adidas_runner"),
    ]
    
    print("📁 Creando estructura de directorios...\n")
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path.absolute()}")
    
    # Información del producto
    print("\n" + "="*70)
    print("📦 INFORMACIÓN DEL PRODUCTO")
    print("="*70 + "\n")
    
    product_info = {
        "name": "Adidas Runner",
        "brand": "Adidas",
        "colors": "Navy Blue / White",
        "size": "42",
        "price": "125.99 USD (12599 centavos)",
        "color_codes": {
            "primary": "Navy Blue (RGB: 0, 51, 102)",
            "secondary": "White (RGB: 255, 255, 255)"
        }
    }
    
    for key, value in product_info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    • {k}: {v}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n" + "="*70)
    print("📸 INSTRUCCIONES PARA IMÁGENES")
    print("="*70 + "\n")
    
    print("""
Tienes 6 imágenes de referencia del Adidas Runner.

📍 COLOCA LAS IMÁGENES AQUÍ:
   📂 assets/images/adidas_runner/

🎯 NOMBRA LAS IMÁGENES ASÍ:
   adidas_runner_001.jpg
   adidas_runner_002.jpg
   adidas_runner_003.jpg
   (etc...)

✅ MÍNIMO RECOMENDADO: 20-30 imágenes
⭐ ÓPTIMO: 50-100 imágenes

📷 CAPTURA IMÁGENES DE:
   ✓ Ángulos diferentes (frontal, lateral, trasera)
   ✓ Diferentes altitudes
   ✓ Diferentes iluminaciones
   ✓ Diferentes fondos
    """)
    
    print("="*70)
    print("🚀 PRÓXIMOS PASOS")
    print("="*70 + "\n")
    
    print("""
1. Ve a frontend: http://localhost:4200
   
2. Copia las 6 imágenes a:
   📂 assets/images/adidas_runner/
   
3. Abre el navegador y crea el producto:
   📦 Products > Create New Product
   
   Datos:
   • Nombre: Adidas Runner
   • Marca: Adidas
   • Colores: Navy Blue / White
   • Talla: 42
   • Stock: 10
   • Precio: 12599 (en centavos)
   
4. Sube las imágenes del producto
   
5. Entrena el modelo YOLO:
   🎓 Training > Train New Model
   
6. Prueba en tiempo real:
   🔍 Detection > Start Real-Time Detection

📚 Para más detalles, lee:
   📄 ADIDAS_RUNNER_TRAINING_GUIDE.md
    """)
    
    print("\n" + "="*70)
    print("✅ SETUP COMPLETADO")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    setup()
