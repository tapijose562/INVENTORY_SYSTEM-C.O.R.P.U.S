"""
Corpus Detector Service - Wrapper para el modelo YOLO entrenado
Proporciona interfaz unificada para detección de objetos con corpus detector
"""

import os
import torch
import warnings
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

warnings.filterwarnings('ignore')

# Parchear torch.load ANTES de importar ultralytics
original_torch_load = torch.load

def patched_torch_load(f, *args, **kwargs):
    """Cargar sin restricción weights_only"""
    kwargs['weights_only'] = False
    return original_torch_load(f, *args, **kwargs)

torch.load = patched_torch_load

# Importar ultralytics después del parche
from ultralytics import YOLO

class CorpusDetectorService:
    """Servicio de detección con modelo entrenado YOLO Corpus"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializar el servicio de detección
        
        Args:
            model_path: Ruta al modelo .pt. Si no se proporciona, busca en rutas por defecto
        """
        self.model = None
        self.model_path = None
        self.available = False
        self._error_message = None
        
        # Buscar modelo en rutas por defecto si no se proporciona
        if model_path is None:
            possible_paths = [
                "corpus_detector.pt",
                "backend/corpus_detector.pt",
                "./corpus_detector.pt",
                os.path.join(os.path.dirname(__file__), "../../corpus_detector.pt"),
                os.path.join(os.getcwd(), "corpus_detector.pt"),
                os.path.join(os.getcwd(), "backend", "corpus_detector.pt"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
        
        # Intentar cargar el modelo
        if model_path and os.path.exists(model_path):
            try:
                self._load_model(model_path)
            except Exception as e:
                self._error_message = f"Error al cargar modelo: {str(e)}"
                print(f"❌ {self._error_message}")
        else:
            self._error_message = f"Modelo no encontrado en: {model_path}"
            print(f"⚠️ {self._error_message}")
        
        # Mapeo de clases (ajustar según tu modelo)
        self.classes = {
            0: "marca",
            1: "shoe",
            2: "texto",
            3: "object"
        }
    
    def _load_model(self, model_path: str):
        """Cargar el modelo YOLO"""
        print(f"📦 Cargando modelo Corpus desde: {model_path}")
        self.model = YOLO(model_path)
        self.model_path = model_path
        self.available = True
        print(f"✅ Modelo Corpus cargado exitosamente")
    
    def is_available(self) -> bool:
        """Verificar si el modelo está disponible"""
        return self.available
    
    def get_status(self) -> Dict:
        """Obtener estado del servicio"""
        return {
            "available": self.available,
            "model_path": self.model_path,
            "error": self._error_message
        }
    
    def detect_objects(self, image: np.ndarray, conf: float = 0.3) -> List[Dict]:
        """
        Detectar objetos en una imagen
        
        Args:
            image: Array numpy con la imagen (BGR de OpenCV)
            conf: Confianza mínima para detecciones (0.0-1.0)
        
        Returns:
            Lista de detecciones con formato compatible con el endpoint
        """
        if not self.available or self.model is None:
            print(f"❌ Modelo no disponible. Error: {self._error_message}")
            return []
        
        try:
            # Ejecutar predicción
            results = self.model.predict(image, conf=conf, verbose=False)
            
            if not results or len(results) == 0:
                return []
            
            result = results[0]
            detections = []
            
            # Procesar boxes si existen
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.cpu().numpy()
                
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf_val = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    
                    # Formato compatible con el endpoint
                    detection = {
                        "class": self.classes.get(cls_id, "unknown"),
                        "class_id": cls_id,
                        "confidence": conf_val,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "area": float((x2 - x1) * (y2 - y1)),
                        "is_shoe": self.classes.get(cls_id, "") in ["shoe", "marca"],
                        "center_x": float((x1 + x2) / 2),
                        "center_y": float((y1 + y2) / 2)
                    }
                    detections.append(detection)
            
            print(f"✅ Corpus detector encontró {len(detections)} objeto(s)")
            return detections
            
        except Exception as e:
            print(f"❌ Error durante detección: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_objects_file(self, image_path: str, conf: float = 0.3) -> List[Dict]:
        """
        Detectar objetos desde una ruta de archivo
        
        Args:
            image_path: Ruta a la imagen
            conf: Confianza mínima
        
        Returns:
            Lista de detecciones
        """
        if not os.path.exists(image_path):
            print(f"❌ Archivo de imagen no encontrado: {image_path}")
            return []
        
        import cv2
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ No se pudo leer la imagen: {image_path}")
            return []
        
        return self.detect_objects(image, conf=conf)


# Crear instancia global del servicio
try:
    corpus_detector = CorpusDetectorService()
    print("[corpus_detector_service] ✅ Servicio iniciado correctamente")
except Exception as e:
    print(f"[corpus_detector_service] ❌ Error al iniciar servicio: {e}")
    corpus_detector = CorpusDetectorService()  # Crear instancia sin modelo
