#!/usr/bin/env python
"""
Script de entrenamiento YOLO para dataset Roboflow
Ejecutado desde ml-pipeline con entorno virtual activado
"""

import os
import numpy as np
from ultralytics import YOLO

print("🚀 Iniciando entrenamiento YOLO...")

# Fix numpy compatibility
try:
    np.trapz([1, 2, 3])
    print("✅ numpy.trapz funciona correctamente")
except AttributeError:
    from scipy.integrate import trapezoid
    np.trapz = trapezoid
    print("🔧 Applied numpy.trapz compatibility fix")

print("📁 Directorio actual:", os.getcwd())
print("📊 Archivos en directorio:", os.listdir('.'))

# Verificar que el data.yaml existe
data_path = 'corpus-1/data.yaml'
if os.path.exists(data_path):
    print(f"✅ Archivo data.yaml encontrado: {data_path}")
    with open(data_path, 'r') as f:
        print("Contenido del data.yaml:")
        print(f.read())
else:
    print(f"❌ Archivo data.yaml no encontrado: {data_path}")
    exit(1)

# Entrenamiento
print("\n🏃 Iniciando entrenamiento...")
model = YOLO('yolov8n-seg.yaml')
results = model.train(
    data=data_path,
    epochs=10,  # Reducido para prueba
    batch=4,    # Reducido para CPU
    imgsz=416,  # Reducido para CPU
    project='runs',
    name='corpus_v1',
    save=True,
    device='cpu',
    workers=0,  # Sin workers para evitar problemas
    verbose=True
)

print("✅ Entrenamiento completado!")
print(f"📁 Resultados en: runs/corpus_v1/")