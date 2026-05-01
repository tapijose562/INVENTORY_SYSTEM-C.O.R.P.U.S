#!/usr/bin/env python3
"""Test YOLO loading directly"""
import torch
import sys
import os

print("PyTorch version:", torch.__version__)
print("=" * 70)

# ============================================================================
# CRITICAL: Fix PyTorch 2.6+ weights_only issue
# ============================================================================
print("\n🔧 Aplicando parche para PyTorch 2.6+...")

_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that falls back to weights_only=False"""
    try:
        return _original_torch_load(f, *args, **kwargs)
    except Exception as e:
        if "weights only" in str(e).lower() or "Unsupported global" in str(e):
            print("   [TORCH] Retrying with weights_only=False...")
            try:
                return _original_torch_load(f, *args, weights_only=False, **kwargs)
            except TypeError:
                return _original_torch_load(f, *args, **kwargs)
        raise

torch.load = _patched_torch_load

# Agregar safe_globals
try:
    import ultralytics.nn.tasks
    safe_modules = [ultralytics.nn.tasks.DetectionModel]
    try:
        safe_modules.extend([
            ultralytics.nn.tasks.SegmentationModel,
            ultralytics.nn.tasks.ClassificationModel,
            ultralytics.nn.tasks.PoseModel,
        ])
    except:
        pass
    torch.serialization.add_safe_globals(safe_modules)
    print("   ✅ PyTorch configurado")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test 1: Load with default path
print("\n1️⃣  Intento 1: Cargar desde models/yolov8n.pt...")
try:
    from pathlib import Path
    model_path = Path("backend/models/yolov8n.pt")
    if model_path.exists():
        print(f"   ✅ Archivo existe: {model_path} ({model_path.stat().st_size / 1e6:.1f} MB)")
    else:
        print(f"   ❌ Archivo no existe: {model_path}")
        model_path = "models/yolov8n.pt"
        if Path(model_path).exists():
            print(f"   ✅ Encontrado en: {model_path}")
    
    from ultralytics import YOLO
    model = YOLO(str(model_path))
    print(f"   ✅ YOLO cargado exitosamente")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test 2: Load default yolov8n
print("\n2️⃣  Intento 2: Cargar yolov8n.pt (descarga si no existe)...")
try:
    model = YOLO("yolov8n.pt", task='detect')
    print(f"   ✅ YOLO yolov8n cargado exitosamente")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test 3: Test detection on simple image
print("\n3️⃣  Probando detección con imagen de prueba...")
try:
    import cv2
    import numpy as np
    
    # Create simple test image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (50, 50), (350, 250), (0, 100, 200), -1)
    cv2.putText(img, "TEST", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    
    if model:
        results = model(img)
        print(f"   ✅ Detección completada: {len(results)} resultado(s)")
        if results:
            print(f"      Detecciones: {len(results[0].boxes)} objeto(s)")
    else:
        print(f"   ⚠️  Modelo no cargado, saltando test")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

print("\n" + "=" * 70)
print("✅ TEST DE YOLO COMPLETADO")
