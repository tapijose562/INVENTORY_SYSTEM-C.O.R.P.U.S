#!/usr/bin/env python
"""
Script simplificado para entrenar YOLO con dataset Roboflow
Usa subprocess para evitar problemas de importación
"""

import subprocess
import sys
import os
from pathlib import Path

def run_training():
    """Ejecuta el entrenamiento usando subprocess"""

    # Comando de entrenamiento
    cmd = [
        sys.executable, "-c", """
import os
import numpy as np
from ultralytics import YOLO

# Fix numpy compatibility
try:
    np.trapz([1, 2, 3])
except AttributeError:
    from scipy.integrate import trapezoid
    np.trapz = trapezoid
    print("🔧 Applied numpy.trapz compatibility fix")

# Entrenamiento
model = YOLO('yolov8n-seg.yaml')
results = model.train(
    data='corpus-1/data.yaml',
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
"""
    ]

    # Cambiar al directorio ml-pipeline
    os.chdir('ml-pipeline')

    print("🚀 Iniciando entrenamiento...")
    print(f"📊 Comando: {' '.join(cmd)}")
    print(f"📁 Directorio: {os.getcwd()}")
    print()

    try:
        # Ejecutar con timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hora máximo
        )

        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ ¡Entrenamiento exitoso!")
            return True
        else:
            print(f"❌ Entrenamiento falló con código: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Entrenamiento timeout (1 hora)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_training()
    sys.exit(0 if success else 1)