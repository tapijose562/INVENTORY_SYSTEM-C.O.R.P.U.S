#!/usr/bin/env python
"""
Script para entrenar YOLO con descarga limpia del modelo
Soluciona problemas de PyTorch 2.6+ con carga de pesos
"""

import os
import sys
import shutil
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import json

print("🔧 Configurando ambiente...\n")

# Descargar modelo limpio
print("📥 Descargando modelo YOLO v8 limpio desde Ultralytics...")

try:
    from ultralytics import YOLO
    
    # Descargar modelo limpio (se carga desde internet si no existe)
    # Usar weights_only=False si es necesario
    model = YOLO('yolov8n.yaml')  # Usar YAML, no el archivo PT
    print("✅ Modelo YAML descargado\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nIntentando alternativa: instalando versión compatible...\n")
    os.system("pip install --upgrade ultralytics torch torchvision")
    from ultralytics import YOLO
    model = YOLO('yolov8n.yaml')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

IMAGES_BASE_DIR = Path("assets/images")
ADIDAS_DIR = IMAGES_BASE_DIR / "adidas_runner"
NIKE_DIR = IMAGES_BASE_DIR / "nike"

DATASET_DIR = Path("data/training_dataset")
MODELS_DIR = Path("models")

CLASSES = {
    0: "adidas_runner",
    1: "nike"
}

# ============================================================================
# FUNCIONES
# ============================================================================

def create_yolo_annotation(image_path, class_id, output_txt_path):
    """Crea anotación YOLO para una imagen"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return False
        
        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            x_center, y_center = 0.5, 0.5
            box_width, box_height = 0.85, 0.85
        else:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            x_center = (x + w/2) / width
            y_center = (y + h/2) / height
            box_width = w / width
            box_height = h / height
            x_center = np.clip(x_center, 0.01, 0.99)
            y_center = np.clip(y_center, 0.01, 0.99)
            box_width = np.clip(box_width, 0.01, 0.99)
            box_height = np.clip(box_height, 0.01, 0.99)
        
        with open(output_txt_path, 'w') as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")
        return True
    except:
        return False

def prepare_dataset():
    """Prepara dataset en formato YOLO"""
    
    print("\n" + "="*70)
    print("📦 PREPARANDO DATASET")
    print("="*70)
    
    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    
    images_train = DATASET_DIR / "images" / "train"
    images_val = DATASET_DIR / "images" / "val"
    labels_train = DATASET_DIR / "labels" / "train"
    labels_val = DATASET_DIR / "labels" / "val"
    
    for p in [images_train, images_val, labels_train, labels_val]:
        p.mkdir(parents=True, exist_ok=True)
    
    all_images = []
    
    if ADIDAS_DIR.exists():
        adidas_imgs = list(ADIDAS_DIR.glob("*.png")) + list(ADIDAS_DIR.glob("*.jpg"))
        print(f"\n🔵 Adidas Runner: {len(adidas_imgs)} imágenes")
        for img in adidas_imgs:
            all_images.append((img, 0, "adidas"))
            print(f"   ✓ {img.name}")
    
    if NIKE_DIR.exists():
        nike_imgs = list(NIKE_DIR.glob("*.PNG")) + list(NIKE_DIR.glob("*.png")) + list(NIKE_DIR.glob("*.jpg"))
        print(f"\n⚪ Nike: {len(nike_imgs)} imágenes")
        for img in nike_imgs:
            all_images.append((img, 1, "nike"))
            print(f"   ✓ {img.name}")
    
    if not all_images:
        print("❌ Sin imágenes")
        return False
    
    print(f"\n📊 Total: {len(all_images)} imágenes")
    
    # Split
    np.random.seed(42)
    indices = np.random.permutation(len(all_images))
    split = int(0.8 * len(all_images))
    train_idx = indices[:split]
    val_idx = indices[split:]
    
    print(f"   Train: {len(train_idx)}, Val: {len(val_idx)}")
    
    # Copiar train
    print("\n📝 Training set...")
    for idx in train_idx:
        img_path, cls_id, _ = all_images[idx]
        shutil.copy2(img_path, images_train / img_path.name)
        txt_path = labels_train / (img_path.stem + ".txt")
        create_yolo_annotation(img_path, cls_id, txt_path)
    
    # Copiar val
    print("📝 Validation set...")
    for idx in val_idx:
        img_path, cls_id, _ = all_images[idx]
        shutil.copy2(img_path, images_val / img_path.name)
        txt_path = labels_val / (img_path.stem + ".txt")
        create_yolo_annotation(img_path, cls_id, txt_path)
    
    # data.yaml
    yaml_content = f"""path: {DATASET_DIR.absolute()}
train: images/train
val: images/val
nc: 2
names:
  0: adidas_runner
  1: nike
"""
    yaml_path = DATASET_DIR / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Dataset: {DATASET_DIR}")
    return DATASET_DIR

def train():
    """Entrena YOLO"""
    
    print("\n" + "="*70)
    print("🤖 ENTRENANDO YOLO v8")
    print("="*70)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n🚀 Iniciando entrenamiento...\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = model.train(
        data=str(DATASET_DIR / "data.yaml"),
        epochs=20,
        imgsz=640,
        batch=2,
        patience=10,
        device='cpu',
        project=str(MODELS_DIR),
        name=f"shoe_detection_{timestamp}",
        exist_ok=False,
        verbose=True,
        save=True,
        augment=True,
    )
    
    print("\n" + "="*70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("="*70)
    
    model_path = MODELS_DIR / f"shoe_detector_{timestamp}.pt"
    model.save(str(model_path))
    print(f"\n📦 Modelo: {model_path}")
    
    return model

def validate(model):
    """Valida detecciones"""
    
    if model is None:
        return {}
    
    print("\n" + "="*70)
    print("✅ VALIDANDO DETECCIONES")
    print("="*70)
    
    results = {}
    
    if ADIDAS_DIR.exists():
        print("\n🔵 Adidas Runner:")
        adidas_imgs = list(ADIDAS_DIR.glob("*.png"))[:2]
        adidas_res = []
        for img_path in adidas_imgs:
            try:
                preds = model.predict(str(img_path), conf=0.3)
                if preds and len(preds[0].boxes) > 0:
                    for box in preds[0].boxes:
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        name = CLASSES.get(cls, "unknown")
                        adidas_res.append({"image": img_path.name, "detected": name, "conf": round(conf, 3)})
                        print(f"   ✓ {img_path.name}: {name} ({conf:.1%})")
                else:
                    print(f"   ⚠ {img_path.name}: No detectado")
            except Exception as e:
                print(f"   ✗ Error: {str(e)[:50]}")
        results["adidas"] = adidas_res
    
    if NIKE_DIR.exists():
        print("\n⚪ Nike:")
        nike_imgs = list(NIKE_DIR.glob("*.PNG"))[:2]
        nike_res = []
        for img_path in nike_imgs:
            try:
                preds = model.predict(str(img_path), conf=0.3)
                if preds and len(preds[0].boxes) > 0:
                    for box in preds[0].boxes:
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        name = CLASSES.get(cls, "unknown")
                        nike_res.append({"image": img_path.name, "detected": name, "conf": round(conf, 3)})
                        print(f"   ✓ {img_path.name}: {name} ({conf:.1%})")
                else:
                    print(f"   ⚠ {img_path.name}: No detectado")
            except Exception as e:
                print(f"   ✗ Error: {str(e)[:50]}")
        results["nike"] = nike_res
    
    return results

def main():
    print("\n╔" + "="*68 + "╗")
    print("║" + "  🚀 ENTRENAMIENTO YOLO - NIKE & ADIDAS 🚀".center(68) + "║")
    print("╚" + "="*68 + "╝\n")
    
    dataset = prepare_dataset()
    if not dataset:
        print("❌ Error")
        return False
    
    model_trained = train()
    
    validation = validate(model_trained)
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"\n✅ Dataset: {DATASET_DIR}")
    print(f"✅ Modelos: {MODELS_DIR}")
    print(f"\n📈 Resultados:\n{json.dumps(validation, indent=2)}")
    
    return True

if __name__ == "__main__":
    main()
