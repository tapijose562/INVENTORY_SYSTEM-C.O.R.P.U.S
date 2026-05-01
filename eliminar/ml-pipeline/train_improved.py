#!/usr/bin/env python
"""
Script de entrenamiento YOLO mejorado con manejo de PyTorch 2.6+
Permite cargar pesos sin restricción weights_only
"""

import os
import torch
import numpy as np
from ultralytics import YOLO

print("🚀 Iniciando entrenamiento YOLO mejorado...")

# Fix numpy compatibility
try:
    np.trapz([1, 2, 3])
    print("✅ numpy.trapz funciona correctamente")
except AttributeError:
    from scipy.integrate import trapezoid
    np.trapz = trapezoid
    print("🔧 Applied numpy.trapz compatibility fix")

# Permitir cargar pesos con PyTorch 2.6+
torch.serialization.add_safe_globals([
    'ultralytics.nn.tasks.SegmentationModel',
    'ultralytics.nn.tasks.DetectionModel',
    'ultralytics.nn.tasks.PoseModel',
    'ultralytics.nn.tasks.ClassificationModel'
])

print("📁 Directorio actual:", os.getcwd())

# Verificar que el data.yaml existe
data_path = 'corpus-1/data.yaml'
if os.path.exists(data_path):
    print(f"✅ Archivo data.yaml encontrado: {data_path}")
else:
    print(f"❌ Archivo data.yaml no encontrado: {data_path}")
    exit(1)

# Entrenamiento
print("\n🏃 Iniciando entrenamiento...")
model = YOLO('yolov8n-seg.yaml')
results = model.train(
    data=data_path,
    epochs=10,
    batch=4,
    imgsz=416,
    project='runs',
    name='corpus_final',
    save=True,
    device='cpu',
    workers=0,
    verbose=True
)

print("✅ Entrenamiento completado!")
print(f"📁 Resultados en: runs/corpus_final/")

# Verificar que el modelo se guardó
best_model_path = 'runs/corpus_final/weights/best.pt'
if os.path.exists(best_model_path):
    print(f"✅ Modelo entrenado guardado en: {best_model_path}")
    print(f"📊 Tamaño del modelo: {os.path.getsize(best_model_path) / 1024 / 1024:.2f} MB")
else:
    print(f"⚠️ Modelo no encontrado en: {best_model_path}")