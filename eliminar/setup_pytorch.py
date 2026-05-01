#!/usr/bin/env python
"""
Script para configurar PyTorch correctamente antes de usar YOLO
"""

import sys
import os

# Configurar PyTorch antes de cualquier otra cosa
os.environ['TORCH_SERIALIZATION'] = 'safe'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Solucionar problema de PyTorch 2.6
try:
    import torch
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
    print("✅ PyTorch configurado correctamente")
except:
    print("⚠ No se pudo configurar PyTorch, intentando alternativa...")
    try:
        import ultralytics
        ultralytics.__version__
        print("✅ Ultralytics disponible")
    except:
        print("⚠ Instalando ultralytics...")
        os.system("pip install --upgrade ultralytics ultralytics")

if __name__ == "__main__":
    print("\nAmbiente PyTorch listo. Ejecuta: python train_shoe_model_v2.py")
