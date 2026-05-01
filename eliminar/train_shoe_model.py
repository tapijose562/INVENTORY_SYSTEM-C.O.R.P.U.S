#!/usr/bin/env python
"""
Script para entrenar YOLO con imágenes de Nike y Adidas Runner
Crea dataset en formato YOLO, entrena el modelo y valida detecciones
"""

import os
import shutil
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from ultralytics import YOLO

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

IMAGES_BASE_DIR = Path("assets/images")
ADIDAS_DIR = IMAGES_BASE_DIR / "adidas_runner"
NIKE_DIR = IMAGES_BASE_DIR / "nike"

DATASET_DIR = Path("data/training_dataset")
MODELS_DIR = Path("models")

# Clases para el modelo YOLO
CLASSES = {
    0: "adidas_runner",
    1: "nike"
}

CLASS_IDS = {v: k for k, v in CLASSES.items()}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def clear_directory(path):
    """Limpia una carpeta"""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

def create_yolo_annotation(image_path, class_id, output_txt_path):
    """
    Crea anotación YOLO para una imagen
    Asume que el zapato ocupa la mayor parte de la imagen
    Formato YOLO: class_id x_center y_center width height (normalizados 0-1)
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return False
    
    height, width = img.shape[:2]
    
    # Detectar el objeto (zapato) usando contornos simples
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar threshold
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Si no hay contornos, usar la imagen completa (aproximado)
        x_center = 0.5
        y_center = 0.5
        box_width = 0.9
        box_height = 0.9
    else:
        # Usar el contorno más grande (el zapato)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Normalizar coordenadas YOLO (0-1)
        x_center = (x + w/2) / width
        y_center = (y + h/2) / height
        box_width = w / width
        box_height = h / height
        
        # Limitar a rango válido
        x_center = np.clip(x_center, 0.01, 0.99)
        y_center = np.clip(y_center, 0.01, 0.99)
        box_width = np.clip(box_width, 0.01, 0.99)
        box_height = np.clip(box_height, 0.01, 0.99)
    
    # Escribir archivo YOLO
    with open(output_txt_path, 'w') as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")
    
    return True

def prepare_dataset():
    """Prepara el dataset en formato YOLO"""
    
    print("\n" + "="*70)
    print("📦 PREPARANDO DATASET EN FORMATO YOLO")
    print("="*70)
    
    # Limpiar dataset anterior
    clear_directory(DATASET_DIR)
    
    # Crear estructura de carpetas
    images_train = DATASET_DIR / "images" / "train"
    images_val = DATASET_DIR / "images" / "val"
    labels_train = DATASET_DIR / "labels" / "train"
    labels_val = DATASET_DIR / "labels" / "val"
    
    for dir_path in [images_train, images_val, labels_train, labels_val]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Recopilar imágenes
    all_images = []
    
    # Adidas Runner
    if ADIDAS_DIR.exists():
        adidas_imgs = list(ADIDAS_DIR.glob("*.jpg")) + list(ADIDAS_DIR.glob("*.png"))
        print(f"\n🔵 Adidas Runner: {len(adidas_imgs)} imágenes encontradas")
        for img_path in adidas_imgs:
            all_images.append((img_path, 0, "adidas_runner"))  # class_id=0
            print(f"   ✓ {img_path.name}")
    
    # Nike
    if NIKE_DIR.exists():
        nike_imgs = list(NIKE_DIR.glob("*.jpg")) + list(NIKE_DIR.glob("*.png"))
        print(f"\n⚪ Nike: {len(nike_imgs)} imágenes encontradas")
        for img_path in nike_imgs:
            all_images.append((img_path, 1, "nike"))  # class_id=1
            print(f"   ✓ {img_path.name}")
    
    if not all_images:
        print("\n❌ No se encontraron imágenes en las carpetas")
        return False
    
    print(f"\n📊 Total de imágenes: {len(all_images)}")
    
    # Dividir en train/val (80/20)
    np.random.seed(42)
    indices = np.random.permutation(len(all_images))
    split = int(0.8 * len(all_images))
    train_indices = indices[:split]
    val_indices = indices[split:]
    
    print(f"   Training: {len(train_indices)} imágenes")
    print(f"   Validation: {len(val_indices)} imágenes")
    
    # Procesar imágenes de entrenamiento
    print("\n📝 Procesando imágenes de entrenamiento...")
    for idx in train_indices:
        img_path, class_id, class_name = all_images[idx]
        
        # Copiar imagen
        dst_img = images_train / img_path.name
        shutil.copy2(img_path, dst_img)
        
        # Crear anotación
        txt_name = img_path.stem + ".txt"
        dst_txt = labels_train / txt_name
        
        if create_yolo_annotation(img_path, class_id, dst_txt):
            print(f"   ✓ {img_path.name} ({class_name})")
        else:
            print(f"   ⚠ {img_path.name} (anotación aproximada)")
    
    # Procesar imágenes de validación
    print("\n📝 Procesando imágenes de validación...")
    for idx in val_indices:
        img_path, class_id, class_name = all_images[idx]
        
        # Copiar imagen
        dst_img = images_val / img_path.name
        shutil.copy2(img_path, dst_img)
        
        # Crear anotación
        txt_name = img_path.stem + ".txt"
        dst_txt = labels_val / txt_name
        
        if create_yolo_annotation(img_path, class_id, dst_txt):
            print(f"   ✓ {img_path.name} ({class_name})")
        else:
            print(f"   ⚠ {img_path.name} (anotación aproximada)")
    
    # Crear archivo data.yaml
    data_yaml = f"""path: {DATASET_DIR.absolute()}
train: images/train
val: images/val
nc: 2
names:
  0: adidas_runner
  1: nike
"""
    
    yaml_path = DATASET_DIR / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(data_yaml)
    
    print(f"\n✅ Dataset preparado en: {DATASET_DIR.absolute()}")
    print(f"✅ Configuración guardada en: {yaml_path}")
    
    return DATASET_DIR

def train_yolo_model(dataset_dir):
    """Entrena el modelo YOLO"""
    
    print("\n" + "="*70)
    print("🤖 ENTRENANDO MODELO YOLO v8")
    print("="*70)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar modelo base (nano es más rápido para este dataset pequeño)
    print("\n📥 Cargando modelo base YOLO v8 Nano...")
    import torch
    torch.serialization.add_safe_globals([])
    model = YOLO('yolov8n.pt', task='detect')
    
    # Entrenar
    print("\n🚀 Iniciando entrenamiento...\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = model.train(
        data=str(DATASET_DIR / "data.yaml"),
        epochs=50,
        imgsz=640,
        batch=4,  # Batch pequeño por dataset pequeño
        patience=10,
        device=0,  # GPU si está disponible, sino CPU
        project=str(MODELS_DIR),
        name=f"shoe_detection_{timestamp}",
        exist_ok=False,
        verbose=True,
        save=True,
        augment=True,
        flipud=0.5,
        fliplr=0.5,
        mosaic=0.5
    )
    
    print("\n" + "="*70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("="*70)
    
    # Guardar modelo entrenado
    model_path = MODELS_DIR / f"shoe_detector_{timestamp}.pt"
    model.save(str(model_path))
    print(f"\n📦 Modelo guardado en: {model_path}")
    
    return model, results

def validate_detections(model):
    """Valida detecciones en las imágenes originales"""
    
    print("\n" + "="*70)
    print("✅ VALIDANDO DETECCIONES")
    print("="*70)
    
    validation_results = {}
    
    # Probar con Adidas Runner
    if ADIDAS_DIR.exists():
        print("\n🔵 Probando con Adidas Runner:")
        adidas_imgs = list(ADIDAS_DIR.glob("*.jpg")) + list(ADIDAS_DIR.glob("*.png"))
        adidas_results = []
        
        for img_path in adidas_imgs[:3]:  # Primeras 3 imágenes
            results = model.predict(str(img_path), conf=0.5)
            
            if results and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = CLASSES.get(cls, "unknown")
                    adidas_results.append({
                        "image": img_path.name,
                        "detected_class": class_name,
                        "confidence": round(conf, 3)
                    })
                    print(f"   ✓ {img_path.name}: {class_name} ({conf:.1%})")
            else:
                print(f"   ⚠ {img_path.name}: No detectado")
        
        validation_results["adidas_runner"] = adidas_results
    
    # Probar con Nike
    if NIKE_DIR.exists():
        print("\n⚪ Probando con Nike:")
        nike_imgs = list(NIKE_DIR.glob("*.jpg")) + list(NIKE_DIR.glob("*.png"))
        nike_results = []
        
        for img_path in nike_imgs[:2]:  # Primeras 2 imágenes
            results = model.predict(str(img_path), conf=0.5)
            
            if results and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = CLASSES.get(cls, "unknown")
                    nike_results.append({
                        "image": img_path.name,
                        "detected_class": class_name,
                        "confidence": round(conf, 3)
                    })
                    print(f"   ✓ {img_path.name}: {class_name} ({conf:.1%})")
            else:
                print(f"   ⚠ {img_path.name}: No detectado")
        
        validation_results["nike"] = nike_results
    
    return validation_results

def main():
    """Función principal"""
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🚀 ENTRENAMIENTO YOLO - NIKE vs ADIDAS RUNNER 🚀".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Paso 1: Preparar dataset
    print("\n📋 PASO 1: PREPARAR DATASET")
    dataset_dir = prepare_dataset()
    if not dataset_dir:
        print("\n❌ No se pudo preparar el dataset")
        return False
    
    # Paso 2: Entrenar modelo
    print("\n📋 PASO 2: ENTRENAR MODELO")
    model, results = train_yolo_model(dataset_dir)
    
    # Paso 3: Validar detecciones
    print("\n📋 PASO 3: VALIDAR DETECCIONES")
    validation_results = validate_detections(model)
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    print(f"\n✅ Dataset preparado: {dataset_dir.absolute()}")
    print(f"✅ Modelo entrenado en: {MODELS_DIR.absolute()}")
    print(f"\n📈 Resultados de validación:")
    print(json.dumps(validation_results, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("🎯 PRÓXIMOS PASOS:")
    print("="*70)
    print("""
1. Modelo listo para usar en tiempo real
2. Copia el modelo entrenado a: backend/models/
3. Usa en detection: model = YOLO('models/shoe_detector_XXXXXX.pt')
4. Prueba en el frontend con webcam o upload
    """)
    
    return True

if __name__ == "__main__":
    main()
