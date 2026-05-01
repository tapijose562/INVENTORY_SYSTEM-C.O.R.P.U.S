#!/usr/bin/env python
"""
Entrenamiento de YOLO v8 con dataset de Roboflow
Clases: marca, shoe, texto
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO

# Fix numpy compatibility issue
import numpy as np
try:
    # Check if trapz exists
    np.trapz([1, 2, 3])
except AttributeError:
    # Monkey patch trapz with trapezoid from scipy
    from scipy.integrate import trapezoid
    np.trapz = trapezoid
    print("🔧 Applied numpy.trapz compatibility fix")

def train_roboflow_model(data_path="ml-pipeline/corpus-1/data.yaml", epochs=50, batch_size=8):
    """
    Entrena modelo YOLO v8 con dataset de Roboflow

    Args:
        data_path (str): Ruta al archivo data.yaml
        epochs (int): Número de épocas de entrenamiento
        batch_size (int): Tamaño del batch
    """

    print("🚀 Iniciando entrenamiento con dataset Roboflow...")
    print(f"📊 Dataset: {data_path}")
    print(f"🎯 Épocas: {epochs}")
    print(f"📦 Batch size: {batch_size}")
    print()

    # Verificar que existe el archivo de configuración
    if not Path(data_path).exists():
        print(f"❌ Error: No se encuentra {data_path}")
        return None

    try:
        # Cargar modelo base para segmentación (las etiquetas son polígonos)
        print("📥 Cargando modelo YOLO v8 nano para segmentación...")
        model = YOLO('yolov8n-seg.yaml')  # Usar modelo de segmentación

        # Configurar entrenamiento
        results = model.train(
            data=data_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=640,
            project="runs",  # Cambiar a runs en lugar de ml-pipeline/runs
            name="corpus_v1",
            save=True,
            save_period=10,  # Guardar cada 10 épocas
            cache=False,  # Desactivar cache para evitar problemas
            device='cpu',  # Usar CPU (cambiar a 0 para GPU si está disponible)
            workers=2,  # Número de workers para data loading
            patience=20,  # Early stopping patience
            verbose=True
        )

        print("✅ Entrenamiento completado!")
        print(f"📁 Resultados guardados en: runs/corpus_v1/")

        # Obtener métricas finales
        metrics = results.results_dict if hasattr(results, 'results_dict') else {}
        print("\n📊 Métricas finales:")
        for key, value in metrics.items():
            print(".4f")

        return results

    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        return None

if __name__ == "__main__":
    # Configuración
    DATA_PATH = "corpus-1/data.yaml"
    EPOCHS = 50
    BATCH_SIZE = 8

    # Ejecutar entrenamiento
    results = train_roboflow_model(DATA_PATH, EPOCHS, BATCH_SIZE)

    if results:
        print("\n🎉 ¡Modelo entrenado exitosamente!")
        print("Para usar el modelo en el backend:")
        print("cp ml-pipeline/runs/corpus_v1/weights/best.pt backend/models/corpus_v1.pt")
    else:
        print("❌ El entrenamiento falló. Revisa los logs anteriores.")
        sys.exit(1)