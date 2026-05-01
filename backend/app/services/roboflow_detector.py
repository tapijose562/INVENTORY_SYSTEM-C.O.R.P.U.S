"""
Roboflow Shoe Detection Service
Specializes in detecting ONLY shoes from the Roboflow trained model
Used exclusively for Real-Time Detection Mode
"""

import os
import numpy as np
import cv2
from typing import List, Dict, Optional
import warnings
import torch
from app.core.config import settings

warnings.filterwarnings('ignore')

# ============================================================================
# CRITICAL: Fix PyTorch 2.6+ weights_only issue for ultralytics YOLO
# ============================================================================
os.environ['TORCH_HOME'] = os.path.join(os.path.dirname(__file__), '..', '..', 'models')

# Monkey-patch torch.load to handle ultralytics models
_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that falls back to weights_only=False for ultralytics"""
    try:
        return _original_torch_load(f, *args, **kwargs)
    except Exception as e:
        if "weights only" in str(e).lower() or "Unsupported global" in str(e):
            try:
                return _original_torch_load(f, *args, weights_only=False, **kwargs)
            except TypeError:
                return _original_torch_load(f, *args, **kwargs)
        raise

# Apply patch
torch.load = _patched_torch_load

# Add safe globals
try:
    import ultralytics.nn.tasks
    safe_modules = [ultralytics.nn.tasks.DetectionModel]
    try:
        safe_modules.extend([
            ultralytics.nn.tasks.SegmentationModel,
            ultralytics.nn.tasks.ClassificationModel,
            ultralytics.nn.tasks.PoseModel,
            ultralytics.nn.tasks.OBBModel
        ])
    except:
        pass
    torch.serialization.add_safe_globals(safe_modules)
except:
    pass

from ultralytics import YOLO


class RoboflowShoeDetector:
    """
    Detector optimized for Roboflow-trained model that detects shoes specifically
    Only used in Real-Time Detection Mode for live camera feed
    """
    
    def __init__(self):
        self.model = None
        self.shoe_classes = ['shoe', 'shoes', 'sneaker', 'sneakers']  # Shoe class variations
        self._load_model()
    
    def _load_model(self):
        """Load Roboflow model or fallback to YOLO nano - optimized for CPU"""
        try:
            # Detectar dispositivo disponible
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"[Roboflow] Using device: {device}")
            
            # Preferir modelo configurado por settings (por ejemplo, el modelo entrenado que subas)
            configured_path = None
            try:
                configured_path = settings.YOLO_MODEL_PATH
            except Exception:
                configured_path = None

            if configured_path:
                # Normalizar ruta relativa a la raíz del backend si es necesario
                candidate = configured_path
                if not os.path.isabs(candidate):
                    candidate = os.path.join(os.path.dirname(__file__), '..', '..', candidate)
                    candidate = os.path.normpath(candidate)

                if os.path.exists(candidate):
                    self.model = YOLO(candidate)
                    self.model.to(device)
                    print(f"[Roboflow] ✅ Using configured YOLO model on {device}: {candidate}")
                    return

            # Try to load Roboflow model if available at the legacy path
            roboflow_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'models', 'roboflow_shoes.pt'
            )

            if os.path.exists(roboflow_path):
                self.model = YOLO(roboflow_path)
                self.model.to(device)
                print(f"[Roboflow] ✅ Roboflow shoe model loaded on {device}: {roboflow_path}")
                return
            
            # Fallback: Use YOLO nano optimized for real-time and CPU
            self.model = YOLO("yolov8n.pt")
            self.model.to(device)
            print(f"[Roboflow] ✅ YOLO nano loaded on {device} (real-time optimized)")
            
        except Exception as e:
            print(f"[Roboflow] ⚠️ Error loading model: {e}")
            self.model = None
    
    def is_shoe_class(self, class_name: str) -> bool:
        """Check if detected class is a shoe"""
        class_name_lower = class_name.lower().strip()
        return any(shoe in class_name_lower for shoe in self.shoe_classes)
    
    def detect_shoes_only(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict]:
        """
        Detect ONLY shoes from image
        Returns only shoe detections, filters out other objects
        Optimized for real-time performance
        
        Args:
            image: Input image as numpy array
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of shoe detections with bbox and metadata
        """
        
        if self.model is None:
            return []
        
        try:
            # Run prediction with real-time optimizations and CPU support
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            results = self.model.predict(
                image,
                conf=confidence_threshold,
                iou=0.45,
                max_det=5,  # Limit to 5 detections for speed
                imgsz=416,  # Smaller size for speed
                device=device,
                verbose=False
            )
            
            shoe_detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                # Process each detection
                if result.boxes is not None:
                    for box, conf, cls_id in zip(
                        result.boxes.xyxy, 
                        result.boxes.conf, 
                        result.boxes.cls
                    ):
                        class_name = result.names.get(int(cls_id), "unknown")
                        
                        # ONLY include shoe detections
                        if self.is_shoe_class(class_name):
                            x1, y1, x2, y2 = box.cpu().numpy()
                            bbox = [float(x1), float(y1), float(x2), float(y2)]
                            
                            detection = {
                                'class': 'shoe',  # Normalize to 'shoe'
                                'class_name': class_name,
                                'confidence': float(conf),
                                'bbox': bbox,
                                'area': float((x2 - x1) * (y2 - y1)),
                                'center_x': float((x1 + x2) / 2),
                                'center_y': float((y1 + y2) / 2),
                            }
                            shoe_detections.append(detection)
            
            # Sort by confidence descending
            shoe_detections.sort(key=lambda x: x['confidence'], reverse=True)
            return shoe_detections
            
        except Exception as e:
            print(f"[Roboflow] Error detecting shoes: {e}")
            return []
    
    def process_realtime_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame for real-time detection
        Optimized for speed
        
        Args:
            frame: Input frame from webcam
            
        Returns:
            Dictionary with detection results formatted for frontend
        """
        import time
        start_time = time.time()
        
        shoe_detections = self.detect_shoes_only(frame, confidence_threshold=0.5)
        
        # Format for frontend
        formatted_detections = []
        for detection in shoe_detections:
            formatted_detections.append({
                'bbox': detection['bbox'],
                'class': 'shoe',
                'confidence': round(detection['confidence'], 2),
                'center': {
                    'x': detection['center_x'],
                    'y': detection['center_y']
                }
            })
        
        return {
            'detections': formatted_detections,
            'shoe_count': len(formatted_detections),
            'processing_time': time.time() - start_time
        }


# Singleton instance for real-time detection
_roboflow_detector = None

def get_roboflow_detector() -> RoboflowShoeDetector:
    """Get or create singleton instance"""
    global _roboflow_detector
    if _roboflow_detector is None:
        _roboflow_detector = RoboflowShoeDetector()
    return _roboflow_detector
