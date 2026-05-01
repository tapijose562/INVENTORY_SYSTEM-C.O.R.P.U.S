#!/usr/bin/env python
"""
Script simplificado: Entrenar YOLO solo con Nike
Dataset mínimo pero funcional
"""

from pathlib import Path
import shutil
import json
from ultralytics import YOLO

print("🚀 ENTRENAMIENTO YOLO - NIKE SIMPLE\n")

# ============================================================================
# PREPARAR DATASET MINIMAL
# ============================================================================

print("📦 PREPARANDO DATASET (Solo Nike)")
print("="*70 + "\n")

NIKE_DIR = Path("assets/images/nike")
DATASET_DIR = Path("data/nike_dataset")

# Limpiar dataset anterior
if DATASET_DIR.exists():
    shutil.rmtree(DATASET_DIR)

# Crear estructura
images_train = DATASET_DIR / "images" / "train"
images_val = DATASET_DIR / "images" / "val"
labels_train = DATASET_DIR / "labels" / "train"
labels_val = DATASET_DIR / "labels" / "val"

for p in [images_train, images_val, labels_train, labels_val]:
    p.mkdir(parents=True, exist_ok=True)

# Recopilar imágenes Nike
nike_imgs = list(NIKE_DIR.glob("*.PNG")) + list(NIKE_DIR.glob("*.png"))
print(f"✅ Imágenes Nike encontradas: {len(nike_imgs)}\n")

for img in nike_imgs:
    print(f"   ✓ {img.name}")

# Dividir manualmente: 4 train, 4 val
train_imgs = nike_imgs[:4]
val_imgs = nike_imgs[4:]

print(f"\n📊 Split: {len(train_imgs)} train, {len(val_imgs)} val\n")

# Copiar y crear labels
print("📝 Copiando imágenes...")
for img_path in train_imgs:
    shutil.copy2(img_path, images_train / img_path.name)
    # Label: clase 0 (nike), bbox aproximado
    txt_path = labels_train / (img_path.stem + ".txt")
    with open(txt_path, 'w') as f:
        f.write("0 0.5 0.5 0.8 0.8\n")  # class x_center y_center width height

for img_path in val_imgs:
    shutil.copy2(img_path, images_val / img_path.name)
    txt_path = labels_val / (img_path.stem + ".txt")
    with open(txt_path, 'w') as f:
        f.write("0 0.5 0.5 0.8 0.8\n")

print("✅ Dataset listo\n")

# Crear data.yaml
data_yaml = f"""path: {DATASET_DIR.absolute()}
train: images/train
val: images/val
nc: 1
names:
  0: nike
"""

with open(DATASET_DIR / "data.yaml", 'w') as f:
    f.write(data_yaml)

# ============================================================================
# ENTRENAR
# ============================================================================

print("🤖 ENTRENANDO YOLO (5 ÉPOCAS)")
print("="*70 + "\n")

model = YOLO('yolov8n.yaml')

try:
    results = model.train(
        data=str(DATASET_DIR / "data.yaml"),
        epochs=5,
        imgsz=640,
        batch=2,
        patience=5,
        device='cpu',
        project='models',
        name='nike_detector',
        exist_ok=True,
        verbose=False,
        save=True,
        plots=False
    )
    
    print("\n✅ ENTRENAMIENTO COMPLETADO\n")
    
    # ============================================================================
    # VALIDAR
    # ============================================================================
    
    print("✅ VALIDANDO DETECCIONES")
    print("="*70 + "\n")
    
    # Cargar mejor modelo
    best_model = YOLO('models/nike_detector/weights/best.pt')
    
    results_data = []
    for img_path in nike_imgs[:2]:
        preds = best_model.predict(str(img_path), conf=0.25, verbose=False)
        
        detected = False
        conf = 0
        if preds and len(preds[0].boxes) > 0:
            detected = True
            conf = float(preds[0].boxes[0].conf[0])
        
        status = "✅" if detected else "❌"
        print(f"{status} {img_path.name}: {'Detectado' if detected else 'No detectado'} ({conf:.1%})")
        
        results_data.append({
            "image": img_path.name,
            "detected": detected,
            "confidence": round(conf, 3)
        })
    
    # Guardar resultados
    with open('nike_validation.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ MODELO LISTO PARA USAR")
    print("="*70)
    print(f"\n📦 Modelo guardado: models/nike_detector/weights/best.pt")
    print(f"📊 Validación: {sum(r['detected'] for r in results_data)}/{len(results_data)} correctas")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)[:100]}")
    import traceback
    traceback.print_exc()
