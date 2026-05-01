"""
Integración del modelo YOLO entrenado con el corpus en FastAPI

Uso en el backend:
    from corpus_detector import CorpusDetector
    
    detector = CorpusDetector()
    results = detector.detect(image_path)
"""

import os
from pathlib import Path
import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Tuple
import cv2
import warnings

# Suprimir advertencias innecesarias
warnings.filterwarnings('ignore')

# Cargar con weights_only=False para PyTorch 2.6+
# Esto es seguro porque confiamos en el archivo que generamos
torch.load = lambda f, *args, **kwargs: torch.load.__wrapped__(
    f, *args, weights_only=False, **{k:v for k,v in kwargs.items() if k != 'weights_only'}
)
torch.load.__wrapped__ = torch.load

class CorpusDetector:
    """Detector de zapatos y texto usando modelo YOLO entrenado"""
    
    def __init__(self, model_path: str = "corpus_detector.pt"):
        """
        Inicializar detector con modelo entrenado
        
        Args:
            model_path: Ruta al archivo del modelo .pt
        """
        self.model_path = model_path
        
        # Verificar que el modelo existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        # Cargar modelo con manejo de PyTorch 2.6+
        print(f"📦 Cargando modelo desde: {model_path}")
        try:
            # Intentar carga normal primero
            self.model = YOLO(model_path)
        except Exception as e:
            if "weights_only" in str(e):
                print(f"🔧 Aplicando workaround para PyTorch 2.6+...")
                # Cargar directamente con weights_only=False
                state_dict = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
                self.model = YOLO(model_path)
            else:
                raise
        
        print(f"✅ Modelo cargado exitosamente")
        
        # Clases del modelo
        self.classes = {
            0: "marca",
            1: "shoe",
            2: "texto"
        }
    
    def detect(self, image_path: str, conf: float = 0.5) -> Dict:
        """
        Detectar objetos en una imagen
        
        Args:
            image_path: Ruta a la imagen
            conf: Confianza mínima para detecciones
            
        Returns:
            Diccionario con resultados de detección
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        # Ejecutar detección
        results = self.model.predict(image_path, conf=conf)
        
        # Procesar resultados
        detections = self._process_results(results[0])
        
        return {
            "image_path": image_path,
            "detections": detections,
            "confidence_threshold": conf
        }
    
    def detect_from_array(self, image_array: np.ndarray, conf: float = 0.5) -> Dict:
        """
        Detectar objetos en un array de imagen (numpy)
        
        Args:
            image_array: Array numpy con la imagen
            conf: Confianza mínima para detecciones
            
        Returns:
            Diccionario con resultados de detección
        """
        # Ejecutar detección
        results = self.model.predict(image_array, conf=conf)
        
        # Procesar resultados
        detections = self._process_results(results[0])
        
        return {
            "detections": detections,
            "confidence_threshold": conf
        }
    
    def _process_results(self, result) -> List[Dict]:
        """
        Procesar resultados de YOLO
        
        Args:
            result: Resultado de YOLO
            
        Returns:
            Lista de detecciones procesadas
        """
        detections = []
        
        if result.boxes is None:
            return detections
        
        boxes = result.boxes.cpu().numpy()
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            detection = {
                "class": self.classes.get(cls_id, "unknown"),
                "class_id": cls_id,
                "confidence": conf,
                "bbox": {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                    "width": float(x2 - x1),
                    "height": float(y2 - y1)
                }
            }
            
            # Agregar máscara si está disponible (para segmentación)
            if result.masks is not None:
                mask_idx = len(detections)
                if mask_idx < len(result.masks):
                    detection["has_mask"] = True
            
            detections.append(detection)
        
        return detections


# Ejemplo de uso
if __name__ == "__main__":
    # Crear detector
    detector = CorpusDetector("corpus_detector.pt")
    
    # Detectar en una imagen
    print("\n🔍 Probando detector...")
    
    # Ejemplo: detectar en imagen de prueba
    test_image = "ml-pipeline/corpus-1/valid/images/corpus-1_png.rf.123_jpg.rf.12345.jpg"
    
    if os.path.exists(test_image):
        results = detector.detect(test_image, conf=0.3)
        print(f"\n📊 Detecciones encontradas: {len(results['detections'])}")
        for i, det in enumerate(results['detections'], 1):
            print(f"  {i}. {det['class']} - Confianza: {det['confidence']:.2f}")
    else:
        print(f"⚠️ Imagen de prueba no encontrada: {test_image}")