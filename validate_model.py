#!/usr/bin/env python
"""
Script para validar el modelo entrenado
Prueba detección en imágenes de Nike y Adidas
"""

from pathlib import Path
import json
from ultralytics import YOLO

print("🔍 VALIDADOR DE DETECCIONES YOLO\n")

# Buscar el modelo más reciente
models_dir = Path("models")
if not models_dir.exists():
    print("❌ No hay modelos entrenados aún")
    exit(1)

# Buscar carpetas de entrenamiento
train_dirs = sorted(models_dir.glob("shoe_detection_*"))
if not train_dirs:
    print("❌ No hay directorios de entrenamiento")
    exit(1)

latest_dir = train_dirs[-1]
model_path = latest_dir / "weights" / "best.pt"

if not model_path.exists():
    print(f"❌ Modelo no encontrado en: {model_path}")
    exit(1)

print(f"✅ Modelo encontrado: {model_path}\n")

# Cargar modelo
print("📥 Cargando modelo...")
model = YOLO(str(model_path))
print("✅ Modelo cargado\n")

# Configuración de clases
CLASSES = {
    0: "adidas_runner",
    1: "nike"
}

# Directorios de imágenes
ADIDAS_DIR = Path("assets/images/adidas_runner")
NIKE_DIR = Path("assets/images/nike")

results_summary = {}

# Validar Adidas
if ADIDAS_DIR.exists():
    print("="*70)
    print("🔵 VALIDANDO ADIDAS RUNNER")
    print("="*70)
    
    adidas_imgs = list(ADIDAS_DIR.glob("*.png"))[:3]
    adidas_results = []
    
    for img_path in adidas_imgs:
        try:
            print(f"\n📸 {img_path.name}")
            preds = model.predict(str(img_path), conf=0.25, verbose=False)
            
            if preds and len(preds[0].boxes) > 0:
                for box in preds[0].boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = CLASSES.get(cls, "unknown")
                    
                    adidas_results.append({
                        "image": img_path.name,
                        "detected_as": class_name,
                        "confidence": round(conf, 3),
                        "correct": class_name == "adidas_runner"
                    })
                    
                    status = "✅" if class_name == "adidas_runner" else "⚠️"
                    print(f"   {status} Detectado como: {class_name} ({conf:.1%})")
            else:
                print(f"   ❌ No detectado")
                adidas_results.append({
                    "image": img_path.name,
                    "detected_as": "nothing",
                    "confidence": 0.0,
                    "correct": False
                })
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:60]}")
    
    results_summary["adidas_runner"] = adidas_results

# Validar Nike
if NIKE_DIR.exists():
    print("\n" + "="*70)
    print("⚪ VALIDANDO NIKE")
    print("="*70)
    
    nike_imgs = list(NIKE_DIR.glob("*.PNG"))[:3]
    nike_results = []
    
    for img_path in nike_imgs:
        try:
            print(f"\n📸 {img_path.name}")
            preds = model.predict(str(img_path), conf=0.25, verbose=False)
            
            if preds and len(preds[0].boxes) > 0:
                for box in preds[0].boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = CLASSES.get(cls, "unknown")
                    
                    nike_results.append({
                        "image": img_path.name,
                        "detected_as": class_name,
                        "confidence": round(conf, 3),
                        "correct": class_name == "nike"
                    })
                    
                    status = "✅" if class_name == "nike" else "⚠️"
                    print(f"   {status} Detectado como: {class_name} ({conf:.1%})")
            else:
                print(f"   ❌ No detectado")
                nike_results.append({
                    "image": img_path.name,
                    "detected_as": "nothing",
                    "confidence": 0.0,
                    "correct": False
                })
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:60]}")
    
    results_summary["nike"] = nike_results

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DE VALIDACIÓN")
print("="*70)

total_correct = 0
total_tests = 0

for brand, results in results_summary.items():
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    total_correct += correct
    total_tests += total
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n{brand.upper()}")
    print(f"  Correcto: {correct}/{total} ({accuracy:.1f}%)")
    
    for result in results:
        status = "✅" if result["correct"] else "❌"
        print(f"  {status} {result['image']}: {result['detected_as']} ({result['confidence']})")

overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
print(f"\n{'='*70}")
print(f"🎯 PRECISIÓN GENERAL: {overall_accuracy:.1f}% ({total_correct}/{total_tests})")
print(f"{'='*70}")

# Guardar resultados
results_file = Path("validation_results.json")
with open(results_file, 'w') as f:
    json.dump({
        "model": str(model_path),
        "overall_accuracy": overall_accuracy,
        "results": results_summary
    }, f, indent=2)

print(f"\n✅ Resultados guardados en: {results_file}")
