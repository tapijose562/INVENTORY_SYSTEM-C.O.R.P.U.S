#!/usr/bin/env python
"""
Script para registrar y entrenar el Adidas Runner
Paso 1: Crear el producto
Paso 2: Recopilar imágenes de entrenamiento
Paso 3: Entrenar YOLO
Paso 4: Detectar en tiempo real
"""

import os
import sys
import shutil
from pathlib import Path
import cv2
import base64
import requests
import json
from datetime import datetime

# Configuración
API_URL = "http://localhost:8000/api/v1"
PRODUCT_NAME = "Adidas Runner"
PRODUCT_BRAND = "Adidas"
PRODUCT_COLORS = "Navy Blue / White"
PRODUCT_SIZE = "42"
PRODUCT_PRICE = 12599  # Precio en centavos (125.99 USD)

# Rutas locales
IMAGES_DIR = Path("assets/images/adidas_runner")
TRAINING_IMAGES_DIR = Path("data/raw/adidas_runner")

class AdidasRunnerTrainer:
    def __init__(self):
        self.product_id = None
        self.images_dir = IMAGES_DIR
        self.training_dir = TRAINING_IMAGES_DIR
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.training_dir.mkdir(parents=True, exist_ok=True)
        
    def step_1_register_product(self):
        """Paso 1: Registrar el producto en la BD"""
        print("\n" + "="*60)
        print("PASO 1: REGISTRAR PRODUCTO ADIDAS RUNNER")
        print("="*60)
        
        product_data = {
            "name": PRODUCT_NAME,
            "brand": PRODUCT_BRAND,
            "colors": PRODUCT_COLORS,
            "color_primary": "Navy Blue",
            "color_secondary": "White",
            "size": PRODUCT_SIZE,
            "stock": 10,
            "price": PRODUCT_PRICE,
            "description": "Adidas Runner - Navy Blue with White accents",
            "color_rgb": {"r": 0, "g": 51, "b": 102},
            "yolo_confidence": 0.85,
            "detection_metadata": {
                "shoe_type": "running",
                "material": "mesh",
                "brand": "adidas",
                "model": "runner"
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/products", json=product_data)
            if response.status_code in [200, 201]:
                product = response.json()
                self.product_id = product.get("id")
                print(f"✅ Producto registrado exitosamente!")
                print(f"   ID: {self.product_id}")
                print(f"   Nombre: {product.get('name')}")
                print(f"   Colores: {product.get('colors')}")
                print(f"   Precio: ${product.get('price')}")
                return True
            else:
                print(f"❌ Error al registrar producto: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Excepción al registrar: {str(e)}")
            return False
    
    def step_2_instructions_collect_images(self):
        """Paso 2: Instrucciones para recopilar imágenes"""
        print("\n" + "="*60)
        print("PASO 2: RECOPILAR IMÁGENES DE ENTRENAMIENTO")
        print("="*60)
        
        print("""
📷 INSTRUCCIONES PARA RECOPILAR IMÁGENES:

1. UBICACIÓN: Coloca al menos 20-30 imágenes en:
   📁 assets/images/adidas_runner/
   
2. ÁNGULOS RECOMENDADOS:
   ✓ Vista frontal (desde arriba)
   ✓ Vista lateral izquierda
   ✓ Vista lateral derecha
   ✓ Vista posterior
   ✓ Desde diferentes ángulos (45°, 60°, etc.)
   
3. CONDICIONES DE LUZ:
   ✓ Luz natural
   ✓ Luz artificial
   ✓ Diferentes intensidades de iluminación
   
4. FONDOS:
   ✓ Fondo blanco (como en las imágenes adjuntas)
   ✓ Fondo gris
   ✓ Diferentes fondos
   
5. FORMATO:
   ✓ Nombres: adidas_runner_001.jpg, adidas_runner_002.jpg, etc.
   ✓ Formato: JPG o PNG
   ✓ Resolución: Mínimo 640x480

📝 NOTA: Las imágenes adjuntas ya contienen varias vistas del Adidas Runner.
   Cópialas a la carpeta assets/images/adidas_runner/
        """)
        
        # Verificar imágenes existentes
        existing_images = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        print(f"\n📊 Imágenes encontradas actualmente: {len(existing_images)}")
        for img in existing_images[:5]:
            print(f"   ✓ {img.name}")
        if len(existing_images) > 5:
            print(f"   ... y {len(existing_images) - 5} más")
        
        return True
    
    def step_3_create_detection_logs(self):
        """Paso 3: Crear logs de detección desde las imágenes"""
        print("\n" + "="*60)
        print("PASO 3: CREAR LOGS DE DETECCIÓN")
        print("="*60)
        
        images = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        
        if not images:
            print("⚠️ No hay imágenes en la carpeta. Por favor, copia primero las imágenes.")
            print(f"   Carpeta esperada: {self.images_dir.absolute()}")
            return False
        
        print(f"📸 Procesando {len(images)} imágenes...")
        
        detection_logs = []
        for idx, img_path in enumerate(images, 1):
            try:
                img = cv2.imread(str(img_path))
                if img is None:
                    print(f"⚠️ No se pudo leer: {img_path.name}")
                    continue
                
                # Crear log de detección
                detection_log = {
                    "detected_brand": PRODUCT_BRAND,
                    "detected_color": PRODUCT_COLORS,
                    "detected_size": PRODUCT_SIZE,
                    "detected_text": "ADIDAS-RUNNER-2024",
                    "confidence_score": 0.92 + (idx * 0.001),  # Confianza variable
                    "image_path": str(img_path),
                    "detection_metadata": {
                        "shoe_type": "running",
                        "training_image": True,
                        "collected_at": datetime.now().isoformat()
                    }
                }
                detection_logs.append(detection_log)
                print(f"   ✓ {idx}. {img_path.name}")
            except Exception as e:
                print(f"   ✗ Error procesando {img_path.name}: {str(e)}")
        
        print(f"\n✅ {len(detection_logs)} logs de detección creados")
        return detection_logs
    
    def step_4_training_instructions(self):
        """Paso 4: Instrucciones para entrenar YOLO"""
        print("\n" + "="*60)
        print("PASO 4: ENTRENAR MODELO YOLO")
        print("="*60)
        
        print("""
🤖 ENTRENAMIENTO DEL MODELO YOLO:

OPCIÓN A: VÍA API (Recomendado - desde el Frontend)
────────────────────────────────────────────────
1. Ve a la página de TRAINING en el frontend
2. Selecciona "Train New Model"
3. El sistema automáticamente:
   ✓ Detectará las imágenes del Adidas Runner
   ✓ Creará el dataset de entrenamiento
   ✓ Entrenará 20 épocas
   ✓ Guardará el modelo actualizado

OPCIÓN B: VÍA TERMINAL (Desarrollo)
────────────────────────────────────────────────
Ejecutar en el backend:
$ python -c "
from app.services.yolo_trainer import YOLOTrainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.product import DetectionLog

# Cargar logs de detección
trainer = YOLOTrainer()
# Dataset será preparado automáticamente
trainer.train(epochs=20, imgsz=640, batch_size=16)
"

PARÁMETROS DE ENTRENAMIENTO:
──────────────────────────
• Epochs: 20 (ajustable según necesidad)
• Batch Size: 16
• Image Size: 640x640
• Learning Rate: Por defecto (0.01)
• Patience: 20 (early stopping)

⏱️ TIEMPO ESTIMADO: 3-10 minutos (depende del hardware)

🎯 RESULTADOS ESPERADOS:
──────────────────────
• Precisión (Precision): > 0.90
• Recall: > 0.85
• mAP50: > 0.85
• Modelo guardado en: models/yolov8n_trained.pt
        """)
        
        return True
    
    def step_5_testing_instructions(self):
        """Paso 5: Instrucciones para pruebas en tiempo real"""
        print("\n" + "="*60)
        print("PASO 5: PRUEBA EN TIEMPO REAL")
        print("="*60)
        
        print("""
✅ TESTING DEL MODELO ENTRENADO:

1. VA AL FRONTEND → Página de DETECTION

2. HABILITA "Real-Time Detection Mode (Beta)"
   • Webcam se activará automáticamente
   • El sistema esperará detectar el Adidas Runner
   
3. PRESENTA EL ZAPATO A LA CÁMARA:
   ✓ Acércalo gradualmente
   ✓ Rótalo para mostrar diferentes ángulos
   ✓ Colócalo sobre diferentes superficies
   ✓ Prueba diferentes condiciones de iluminación
   
4. OBSERVA LOS RESULTADOS:
   ├─ Brand: "Adidas" ✓
   ├─ Colors: "Navy Blue / White" ✓
   ├─ Size: Detectado ✓
   ├─ Confidence: > 0.85 ✓
   └─ Price: "$125.99" ✓

5. GUARDAR DETECCIONES CORRECTAS:
   • Cada detección se registra automáticamente
   • Los datos se usan para mejorar el modelo

📊 MÉTRICAS EN PANTALLA:
   • FPS: Fotogramas por segundo
   • Detection Speed: ms por detección
   • Accuracy: Precisión de la detección
   • Detection History: Últimas 10 detecciones
        """)
        
        return True
    
    def run_all_steps(self):
        """Ejecutar todos los pasos"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║  🚀 ENTRENAMIENTO DE ADIDAS RUNNER - INICIO RÁPIDO 🚀  ║")
        print("╚" + "="*58 + "╝")
        
        # Paso 1: Registrar
        if not self.step_1_register_product():
            print("\n❌ Falló el registro del producto. Abortando.")
            return False
        
        # Paso 2: Instrucciones de recopilación
        self.step_2_instructions_collect_images()
        
        # Paso 3: Crear logs
        detection_logs = self.step_3_create_detection_logs()
        if not detection_logs:
            print("\n⚠️ Necesitas imágenes para entrenar. Agrega imágenes primero.")
        
        # Paso 4: Instrucciones de entrenamiento
        self.step_4_training_instructions()
        
        # Paso 5: Instrucciones de testing
        self.step_5_testing_instructions()
        
        print("\n" + "="*60)
        print("RESUMEN COMPLETO")
        print("="*60)
        print(f"""
✅ Producto registrado:
   • ID: {self.product_id}
   • Nombre: {PRODUCT_NAME}
   • Marca: {PRODUCT_BRAND}
   • Colores: {PRODUCT_COLORS}
   
📷 Imágenes de entrenamiento:
   • Ubicación: {self.images_dir.absolute()}
   • Mínimo recomendado: 30 imágenes
   
🤖 Próximo paso:
   1. Copia imágenes a: assets/images/adidas_runner/
   2. Ve al FRONTEND → Training
   3. Inicia el entrenamiento
   4. Una vez completado, ve a Detection
   5. Prueba el "Real-Time Mode"
   
💡 TIPS:
   • Toma fotos desde múltiples ángulos
   • Varía las condiciones de iluminación
   • Usa diferentes fondos
   • Más imágenes = Mejor detección
        """)
        
        return True

if __name__ == "__main__":
    trainer = AdidasRunnerTrainer()
    trainer.run_all_steps()
