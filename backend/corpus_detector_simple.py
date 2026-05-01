"""
Detector YOLO Corpus - Versión simplificada sin problemas de PyTorch 2.6
"""

import os
import sys
import torch
import warnings
warnings.filterwarnings('ignore')

# IMPORTANTE: Parchear torch.load ANTES de importar ultralytics
original_torch_load = torch.load

def patched_torch_load(f, *args, **kwargs):
    """Cargar sin restricción weights_only"""
    kwargs['weights_only'] = False
    return original_torch_load(f, *args, **kwargs)

torch.load = patched_torch_load

# Ahora importar ultralytics
from ultralytics import YOLO
import numpy as np
from typing import List, Dict

class CorpusDetector:
    """Detector YOLO para Corpus - Modelos entrenados"""
    
    def __init__(self, model_path: str = "corpus_detector.pt"):
        """Inicializar detector"""
        self.model_path = model_path
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        print(f"📦 Cargando modelo: {model_path}")
        self.model = YOLO(model_path)
        print(f"✅ Modelo cargado")
        
        self.classes = {
            0: "marca",
            1: "shoe", 
            2: "texto"
        }
    
    def detect(self, image_path: str, conf: float = 0.5) -> Dict:
        """Detectar objetos en imagen"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        results = self.model.predict(image_path, conf=conf)
        return self._process_results(results[0], image_path, conf)
    
    def detect_from_array(self, image_array: np.ndarray, conf: float = 0.5) -> Dict:
        """Detectar en array numpy"""
        results = self.model.predict(image_array, conf=conf)
        return self._process_results(results[0], "array", conf)
    
    def _process_results(self, result, source, conf: float) -> Dict:
        """Procesar resultados YOLO"""
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf_val = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                detections.append({
                    "class": self.classes.get(cls_id, "unknown"),
                    "class_id": cls_id,
                    "confidence": conf_val,
                    "bbox": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                        "width": float(x2 - x1),
                        "height": float(y2 - y1)
                    }
                })
        
        return {
            "source": source,
            "detections": detections,
            "confidence_threshold": conf
        }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("✅ Detector YOLO Corpus importado correctamente")
    print("="*60)
    
    # Probar carga
    if os.path.exists("backend/corpus_detector.pt"):
        print("\n🧪 Probando modelo...")
        try:
            detector = CorpusDetector("backend/corpus_detector.pt")
            print("✅ Modelo listo para usar")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("\n⚠️ Modelo no encontrado en: backend/corpus_detector.pt")