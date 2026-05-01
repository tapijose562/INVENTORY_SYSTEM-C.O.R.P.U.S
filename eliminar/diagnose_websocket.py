#!/usr/bin/env python3
"""
Diagnóstico del WebSocket y servicios de detección
"""

import os
import sys
import torch

print("=" * 60)
print("🔍 DIAGNÓSTICO DE WEBSOCKET Y DETECCIÓN")
print("=" * 60)

# 1. Verificar CUDA/GPU
print("\n1️⃣  VERIFICANDO DISPOSITIVOS:")
print(f"   - CUDA Disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   - GPU: {torch.cuda.get_device_name(0)}")
    print(f"   - CUDA Version: {torch.version.cuda}")
else:
    print("   - ⚠️  SIN GPU - Usando CPU (más lento pero funciona)")

# 2. Verificar YOLO
print("\n2️⃣  VERIFICANDO YOLO:")
try:
    from ultralytics import YOLO
    print("   ✅ YOLO importado correctamente")
    
    # Intentar cargar modelo pequeño
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   - Intentando cargar yolov8n.pt en {device}...")
    model = YOLO("yolov8n.pt")
    model.to(device)
    print(f"   ✅ Modelo YOLO cargado exitosamente en {device}")
except Exception as e:
    print(f"   ❌ Error cargando YOLO: {e}")

# 3. Verificar OpenCV
print("\n3️⃣  VERIFICANDO OPENCV:")
try:
    import cv2
    print(f"   ✅ OpenCV {cv2.__version__} importado")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar FastAPI
print("\n4️⃣  VERIFICANDO FASTAPI:")
try:
    from fastapi import FastAPI, WebSocket
    print("   ✅ FastAPI y WebSocket importados")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Verificar archivo principal
print("\n5️⃣  VERIFICANDO BACKEND MAIN.PY:")
main_path = "backend/main.py"
if os.path.exists(main_path):
    print(f"   ✅ {main_path} existe")
    with open(main_path) as f:
        content = f.read()
        if "/api/v1/detection/ws/real-time-detection" in content:
            print("   ✅ WebSocket endpoint definido correctamente")
        else:
            print("   ❌ WebSocket endpoint NO encontrado")
else:
    print(f"   ❌ {main_path} NO existe")

# 6. Verificar Roboflow detector
print("\n6️⃣  VERIFICANDO ROBOFLOW DETECTOR:")
detector_path = "backend/app/services/roboflow_detector.py"
if os.path.exists(detector_path):
    print(f"   ✅ {detector_path} existe")
    try:
        sys.path.insert(0, 'backend')
        from app.services.roboflow_detector import get_roboflow_detector
        print("   ✅ Detector importado correctamente")
        print("   - Intentando inicializar detector...")
        detector = get_roboflow_detector()
        if detector and detector.model:
            print("   ✅ Detector inicializado exitosamente")
        else:
            print("   ⚠️  Detector cargado pero modelo es None (usará YOLO nano)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print(f"   ❌ {detector_path} NO existe")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
print("\n💡 RECOMENDACIONES:")
print("   1. Si tienes GPU NVIDIA, verifica que CUDA está instalado correctamente")
print("   2. Sin GPU, YOLO usará CPU (será más lento pero funciona)")
print("   3. Asegúrate de que el puerto 8000 no esté siendo usado")
print("   4. Reinicia el backend después de hacer cambios")
