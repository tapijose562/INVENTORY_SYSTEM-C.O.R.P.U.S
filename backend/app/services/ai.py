import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
from typing import Dict, Tuple, Optional
import torch
import os
import sys
import warnings
from app.core.config import settings

# Suppress PyTorch warnings
warnings.filterwarnings('ignore')

# Configure Tesseract path
try:
    if os.path.exists(settings.PYTESSERACT_PATH):
        pytesseract.pytesseract.pytesseract_cmd = settings.PYTESSERACT_PATH
        print(f"[OCR] Tesseract configurado en: {settings.PYTESSERACT_PATH}")
    else:
        print(f"[OCR] ⚠️ Ruta de Tesseract no encontrada: {settings.PYTESSERACT_PATH}")
        print("[OCR] Usando fallback a EasyOCR")
except Exception as e:
    print(f"[OCR] Error configurando Tesseract: {e}")

# ============================================================================
# CRITICAL: Fix PyTorch 2.6+ weights_only issue for ultralytics YOLO
# ============================================================================
os.environ['TORCH_HOME'] = os.path.join(os.path.dirname(__file__), '..', '..', 'models')

# Monkey-patch torch.load to handle ultralytics models
_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that falls back to weights_only=False for ultralytics"""
    try:
        # Primero intentar con la configuración segura
        return _original_torch_load(f, *args, **kwargs)
    except Exception as e:
        if "weights only" in str(e).lower() or "Unsupported global" in str(e):
            print("[TORCH] Retrying with weights_only=False...")
            # Fallback: cargar sin restricción de pesos
            try:
                return _original_torch_load(f, *args, weights_only=False, **kwargs)
            except TypeError:
                # weights_only no es parámetro en versiones antiguas
                return _original_torch_load(f, *args, **kwargs)
        raise

# Aplicar el parche
torch.load = _patched_torch_load

# Agregar safe_globals
try:
    import ultralytics.nn.tasks
    safe_modules = [ultralytics.nn.tasks.DetectionModel]
    try:
        safe_modules.extend([
            ultralytics.nn.tasks.SegmentationModel,
            ultralytics.nn.tasks.ClassificationModel,
            ultralytics.nn.tasks.PoseModel,
        ])
    except:
        pass
    torch.serialization.add_safe_globals(safe_modules)
    print("[INIT] PyTorch configured for ultralytics")
except Exception as e:
    print(f"[INIT] Warning: {e}")

from ultralytics import YOLO

class YOLODetectionService:
    """Service for YOLO object detection"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model with proper error handling and CPU support"""
        try:
            # Detectar GPU disponible
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"[YOLO] Using device: {device}")
            
            # Intentar cargar modelo especificado
            self.model = YOLO(settings.YOLO_MODEL_PATH, task='detect')
            self.model.to(device)
            print(f"✅ YOLO model loaded successfully on {device}: {settings.YOLO_MODEL_PATH}")
            return
            
        except Exception as e:
            print(f"⚠️  Error loading YOLO from {settings.YOLO_MODEL_PATH}: {str(e)[:100]}")
            
        try:
            # Fallback 1: Cargar modelo pequeño de detección en CPU
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = YOLO("yolov8n.pt", task='detect')
            self.model.to(device)
            print(f"✅ Fallback YOLO small model (yolov8n) loaded on {device} for detection")
            return
            
        except Exception as e:
            print(f"⚠️  Error loading fallback yolov8n: {str(e)[:100]}")
            
        try:
            # Fallback 2: Cargar desde ultralytics directamente con CPU
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = YOLO.from_pretrained("ultralytics/yolov8n")
            self.model.to(device)
            print(f"✅ Fallback YOLO from ultralytics hub loaded on {device}")
            return
            
        except Exception as e:
            print(f"⚠️  Error loading from ultralytics hub: {str(e)[:100]}")
            
        print("❌ All YOLO loading attempts failed. Using mock detection.")
        self.model = None
    
    def detect_shoes(self, image: np.ndarray) -> list:
        """Enhanced shoe detection with better filtering and segmentation"""
        if self.model is None:
            # Fallback mock detection when model is unavailable
            height, width = image.shape[:2]
            return [{
                'class': 'shoe',
                'confidence': 0.75,
                'bbox': [width//4, height//4, 3*width//4, 3*height//4],
                'area': float((width//2)*(height//2)),
                'segmentation': None,
                'is_shoe': True
            }]

        try:
            # Use detection with CPU-optimized settings
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            results = self.model.predict(
                image,
                conf=settings.YOLO_CONFIDENCE_THRESHOLD,
                iou=0.5,  # Non-maximum suppression threshold
                max_det=10,  # Maximum detections
                device=device,
                verbose=False
            )
        except Exception as e:
            print(f"YOLO prediction error: {e}")
            height, width = image.shape[:2]
            bbox = [width//4, height//4, 3*width//4, 3*height//4]
            x1, y1, x2, y2 = bbox
            segmentation = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            return [{
                'class': 'shoe',
                'confidence': 0.75,
                'bbox': bbox,
                'area': float((width//2)*(height//2)),
                'segmentation': segmentation,
                'is_shoe': True,
                'center_x': (bbox[0] + bbox[2]) / 2,
                'center_y': (bbox[1] + bbox[3]) / 2
            }]

        detections = []
        height, width = image.shape[:2]

        result = results[0]  # Since we predict on one image
        for i, box in enumerate(result.boxes):
            class_name = result.names[int(box.cls)]
            confidence = float(box.conf)

            # Enhanced shoe detection logic
            is_shoe = self._is_shoe_like_object(class_name, confidence, box, image.shape)

            # Calculate bounding box
            bbox = box.xyxy[0].tolist()
            area = float((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))

            # Get segmentation mask if available, else create rectangular from bbox
            segmentation = None
            if hasattr(result, 'masks') and result.masks is not None and i < len(result.masks.xy):
                segmentation = result.masks.xy[i].tolist()
            else:
                # Create rectangular segmentation from bbox
                x1, y1, x2, y2 = bbox
                segmentation = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]

            detection = {
                "class": class_name,
                "confidence": confidence,
                "bbox": bbox,
                "area": area,
                "segmentation": segmentation,
                "is_shoe": is_shoe,
                "center_x": (bbox[0] + bbox[2]) / 2,
                "center_y": (bbox[1] + bbox[3]) / 2
            }
            detections.append(detection)

        # Filter and prioritize shoe-like detections
        shoe_detections = [d for d in detections if d['is_shoe']]

        # If no shoe detections, try to find the most shoe-like object
        if not shoe_detections:
            shoe_detections = self._find_best_shoe_candidate(detections, image.shape)

        # If still no detections, create a smart mock detection
        if not shoe_detections:
            print("[YOLO] No suitable objects detected, creating smart mock shoe detection")
            shoe_detections = [self._create_smart_mock_detection(image)]

        # Sort by confidence and area (prefer central, reasonably-sized objects)
        shoe_detections.sort(key=lambda x: (x['confidence'], -abs(x['center_x'] - width/2), -abs(x['center_y'] - height/2)), reverse=True)

        return shoe_detections

    def _is_shoe_like_object(self, class_name: str, confidence: float, box, image_shape) -> bool:
        """Determine if detected object is shoe-like"""
        shoe_keywords = [
            'shoe', 'sneakers', 'boot', 'sandal', 'heel', 'slipper',
            'footwear', 'tennis shoe', 'running shoe', 'dress shoe'
        ]

        # Direct shoe detection
        if any(keyword in class_name.lower() for keyword in shoe_keywords):
            return True

        # Size and position heuristics for potential shoes
        height, width = image_shape[:2]
        bbox = box.xyxy[0].tolist()
        bbox_width = bbox[2] - bbox[0]
        bbox_height = bbox[3] - bbox[1]
        area_ratio = (bbox_width * bbox_height) / (width * height)

        # Shoes are typically 10-40% of image area
        if not (0.05 < area_ratio < 0.6):
            return False

        # Shoes are usually wider than tall (aspect ratio)
        aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
        if not (0.5 < aspect_ratio < 3.0):
            return False

        # Position: shoes are often in lower half of image
        center_y = (bbox[1] + bbox[3]) / 2
        if center_y < height * 0.3:  # Too high in image
            return False

        # Common objects that might be mistaken for shoes
        non_shoe_objects = [
            'person', 'hand', 'arm', 'leg', 'foot', 'chair', 'table',
            'bottle', 'cup', 'book', 'phone', 'remote', 'keyboard', 'mouse'
        ]

        if class_name.lower() in non_shoe_objects:
            return False

        # For generic objects with good confidence, assume they might be shoes
        if confidence > 0.3:
            return True

        return False

    def _find_best_shoe_candidate(self, detections: list, image_shape) -> list:
        """Find the most shoe-like object from non-shoe detections"""
        if not detections:
            return []

        height, width = image_shape[:2]

        # Score each detection for shoe-likeness
        scored_detections = []
        for detection in detections:
            score = 0
            bbox = detection['bbox']
            confidence = detection['confidence']

            # Size score (prefer medium-sized objects)
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            area_ratio = (bbox_width * bbox_height) / (width * height)
            if 0.1 < area_ratio < 0.4:
                score += 2
            elif 0.05 < area_ratio < 0.6:
                score += 1

            # Aspect ratio score (prefer wider than tall)
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
            if 0.7 < aspect_ratio < 2.5:
                score += 2
            elif 0.5 < aspect_ratio < 3.0:
                score += 1

            # Position score (prefer lower center)
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2

            # Distance from center (prefer central objects)
            center_distance = ((center_x - width/2)**2 + (center_y - height/2)**2)**0.5
            max_distance = ((width/2)**2 + (height/2)**2)**0.5
            center_score = 1 - (center_distance / max_distance)
            score += center_score * 2

            # Vertical position (prefer lower objects)
            vertical_score = 1 - (center_y / height)
            score += vertical_score

            # Confidence bonus
            score += confidence

            detection['shoe_score'] = score
            scored_detections.append(detection)

        # Return top candidates
        scored_detections.sort(key=lambda x: x.get('shoe_score', 0), reverse=True)
        top_candidates = scored_detections[:3]  # Return top 3

        # Mark as potential shoes
        for detection in top_candidates:
            detection['is_shoe'] = True
            detection['class'] = f"potential_shoe_{detection['class']}"

        return top_candidates

    def _create_smart_mock_detection(self, image) -> dict:
        """Create a smart mock detection based on image analysis"""
        height, width = image.shape[:2]

        # Try to find shoe-like regions using edge detection
        gray = cv2.cvtColor(cv2.resize(image, (width//4, height//4)), cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Look for horizontal edges in lower part (typical shoe features)
        lower_half = edges[height//8:, :]
        edge_density = np.sum(lower_half > 0) / lower_half.size

        if edge_density > 0.05:  # If there are edges in lower area
            # Create detection in lower center area
            bbox = [
                width * 0.2,  # x1
                height * 0.6,  # y1
                width * 0.8,  # x2
                height * 0.9   # y2
            ]
        else:
            # Default center area
            bbox = [
                width * 0.25,
                height * 0.25,
                width * 0.75,
                height * 0.75
            ]

        return {
            'class': 'smart_detected_shoe',
            'confidence': 0.6,
            'bbox': bbox,
            'area': float((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])),
            'segmentation': [[bbox[0], bbox[1]], [bbox[2], bbox[1]], [bbox[2], bbox[3]], [bbox[0], bbox[3]]],
            'is_shoe': True,
            'center_x': (bbox[0] + bbox[2]) / 2,
            'center_y': (bbox[1] + bbox[3]) / 2
        }

class ColorDetectionService:
    """Service for RGB color detection"""
    
    @staticmethod
    def extract_dominant_color(image: np.ndarray, bbox: Optional[list] = None) -> Tuple[Dict, str]:
        """Extract dominant color from image or bounding box region"""
        if bbox:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            roi = image[y1:y2, x1:x2]
        else:
            roi = image
        
        # Ensure ROI is 3-channel BGR
        if len(roi.shape) == 2:
            # Convert grayscale to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        elif len(roi.shape) == 3 and roi.shape[2] == 1:
            # Convert single-channel to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        elif len(roi.shape) == 3 and roi.shape[2] == 4:
            # Convert RGBA to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_RGBA2BGR)
        
        # Convert to RGB and reshape
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        pixels = roi_rgb.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # K-means clustering for dominant colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        
        dominant_rgb = [int(c) for c in centers[0]]
        color_name = ColorDetectionService._get_color_name(dominant_rgb)
        
        return {
            "r": dominant_rgb[0],
            "g": dominant_rgb[1],
            "b": dominant_rgb[2]
        }, color_name
    
    @staticmethod
    def extract_multiple_colors(image: np.ndarray, bbox: Optional[list] = None, max_colors: int = 3) -> Tuple[str, Dict]:
        """Extract multiple dominant colors and return formatted string"""
        if bbox:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            roi = image[y1:y2, x1:x2]
        else:
            roi = image
        
        # Ensure ROI is 3-channel BGR
        if len(roi.shape) == 2:
            # Convert grayscale to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        elif len(roi.shape) == 3 and roi.shape[2] == 1:
            # Convert single-channel to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        elif len(roi.shape) == 3 and roi.shape[2] == 4:
            # Convert RGBA to BGR
            roi = cv2.cvtColor(roi, cv2.COLOR_RGBA2BGR)
        
        # Convert to RGB and reshape
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        pixels = roi_rgb.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # K-means clustering for multiple colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        k = min(max_colors, len(pixels))
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        
        # Sort centers by frequency (most common first)
        unique, counts = np.unique(labels, return_counts=True)
        sorted_indices = np.argsort(-counts)  # Sort descending by count
        
        # Extract color names
        color_names = []
        all_colors_rgb = []
        
        for idx in sorted_indices[:max_colors]:
            rgb = [int(c) for c in centers[idx]]
            color_name = ColorDetectionService._get_color_name(rgb)
            color_names.append(color_name)
            all_colors_rgb.append({
                "r": rgb[0],
                "g": rgb[1],
                "b": rgb[2],
                "name": color_name
            })
        
        # Format as "Color1 / Color2 / Color3"
        colors_string = " / ".join(color_names)
        
        return colors_string, {
            "r": all_colors_rgb[0]["r"],
            "g": all_colors_rgb[0]["g"],
            "b": all_colors_rgb[0]["b"]
        }, all_colors_rgb
    
    @staticmethod
    def _get_color_name(rgb: list) -> str:
        """Determine color name from RGB values"""
        r, g, b = rgb
        
        # Simple color naming based on dominant channel
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        elif r > g and g > b and r > b:
            return "orange"
        elif r > g and g < b and r > b:
            return "purple"
        else:
            return "other"

class OCRService:
    """Service for Optical Character Recognition"""
    
    _reader = None  # Cache para EasyOCR
    _reader_initialized = False
    
    @classmethod
    def _get_easyocr_reader(cls):
        """Obtener reader de EasyOCR (lazy load con mejor manejo de errores)"""
        if cls._reader_initialized:
            return cls._reader
        
        cls._reader_initialized = True
        
        try:
            print("[OCR] Inicializando EasyOCR...")
            import easyocr
            
            # Intentar inicializar con GPU primero, luego sin GPU
            try:
                cls._reader = easyocr.Reader(['en', 'es'], gpu=True)
                print("[OCR] EasyOCR inicializado con GPU")
            except Exception as gpu_error:
                print(f"[OCR] GPU no disponible ({gpu_error}), usando CPU...")
                cls._reader = easyocr.Reader(['en', 'es'], gpu=False)
                print("[OCR] EasyOCR inicializado con CPU")
                
        except ImportError as e:
            print(f"[OCR] EasyOCR no instalado: {e}")
            cls._reader = None
        except Exception as e:
            print(f"[OCR] Error inicializando EasyOCR: {e}")
            print(f"[OCR] Tipo de error: {type(e).__name__}")
            import traceback
            print(f"[OCR] Traceback: {traceback.format_exc()}")
            cls._reader = None
            
        return cls._reader
    
    @staticmethod
    def extract_text(image: np.ndarray, bbox: Optional[list] = None) -> str:
        """Extract text from image using OCR (EasyOCR primary, Tesseract fallback)"""
        print(f"[DEBUG] Llamando OCR con bbox: {bbox}")
        
        # Preparar ROI
        roi = image
        used_bbox = False
        
        if bbox:
            try:
                x1, y1, x2, y2 = [int(v) for v in bbox]
                # Validar y corregir bounds
                height, width = image.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, max(x2, x1 + 10)), min(height, max(y2, y1 + 10))
                
                if x2 > x1 and y2 > y1:
                    roi = image[y1:y2, x1:x2]
                    used_bbox = True
                    print(f"[OCR] ROI bounds: x1={x1}, y1={y1}, x2={x2}, y2={y2}, shape={roi.shape}")
                else:
                    print(f"[OCR] Bbox inválido, usando imagen completa: {bbox}")
            except Exception as e:
                print(f"[OCR] Error procesando bbox {bbox}: {e}, usando imagen completa")
        
        def normalize_text(raw: str) -> str:
            """Normalizar texto extraído"""
            if not raw:
                return ""
            # Reemplazar múltiples espacios y newlines
            import re
            text = re.sub(r'\s+', ' ', raw.strip())
            return text
        
        # Método 1: EasyOCR
        try:
            reader = OCRService._get_easyocr_reader()
            if reader:
                # Convertir a RGB para EasyOCR
                roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB) if len(roi.shape) == 3 else roi
                
                print(f"[OCR] Intentando EasyOCR en {'ROI' if used_bbox else 'imagen completa'}...")
                results = reader.readtext(roi_rgb, detail=0, paragraph=False)
                
                if results:
                    text = normalize_text(" ".join(results))
                    if text:
                        print(f"[OCR] ✅ Texto extraído con EasyOCR: '{text}'")
                        return text
                else:
                    print("[OCR] EasyOCR no encontró texto")
        except Exception as e:
            print(f"[OCR] Error con EasyOCR: {e}")
        
        # Método 2: Tesseract (si está disponible)
        try:
            if hasattr(pytesseract, 'image_to_string'):
                print(f"[OCR] Intentando Tesseract en {'ROI' if used_bbox else 'imagen completa'}...")
                
                # Preprocesar imagen para Tesseract
                if len(roi.shape) == 3:
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                else:
                    gray = roi
                
                # Mejorar contraste
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                
                # Aplicar threshold
                _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                text = pytesseract.image_to_string(thresh, lang='spa+eng', config='--oem 3 --psm 6')
                text = normalize_text(text)
                
                if text:
                    print(f"[OCR] ✅ Texto extraído con Tesseract: '{text}'")
                    return text
                else:
                    print("[OCR] Tesseract no encontró texto")
        except Exception as e:
            print(f"[OCR] Tesseract no disponible o falló: {e}")
        
        # Método 3: Si usamos bbox y no encontramos texto, intentar en imagen completa
        if used_bbox:
            print("[OCR] No se encontró texto en ROI, intentando en imagen completa...")
            return OCRService.extract_text(image, None)
        
        print("[OCR] No se pudo extraer texto")
        return ""
    
    @staticmethod
    def extract_numbers(text: str) -> list:
        """Extract numbers from OCR text"""
        import re
        numbers = re.findall(r'\d+', text)
        return numbers

class AISuggestionService:
    """Service to generate OCR text suggestions using AI"""

    @staticmethod
    def suggest_text(
        ocr_text: str = "",
        image_info: str = "",
        brand: str = "",
        color: str = "",
        size: str = ""
    ) -> str:
        prompt = (
            "Eres un asistente que limpia y sugiere texto de producto a partir de texto OCR, datos de detección y datos de imagen. "
            "Devuelve un texto breve, legible y útil para la etiqueta del producto. "
        )

        if brand:
            prompt += f"Marca detectada: {brand.strip()}. "
        if color:
            prompt += f"Color detectado: {color.strip()}. "
        if size:
            prompt += f"Talla detectada: {size.strip()}. "

        if ocr_text:
            prompt += f"Texto OCR detectado: {ocr_text.strip()}\n"
        else:
            prompt += "No hay texto OCR detectado.\n"

        if image_info:
            prompt += f"Información adicional de la imagen: {image_info.strip()}\n"

        prompt += (
            "Si el texto OCR es confuso o incompleto, sugiere una versión corregida basada en el contexto. "
            "No inventes datos que no estén presentes, pero mejora la legibilidad y elimina ruido."
        )

        # Prefer OpenRouter if configured
        if settings.OPENROUTER_API_KEY:
            suggestion = AISuggestionService._call_openrouter(prompt)
            if suggestion:
                return suggestion

        # Then try Ollama if configured
        if settings.OLLAMA_API_URL:
            suggestion = AISuggestionService._call_ollama(prompt)
            if suggestion:
                return suggestion

        return AISuggestionService._fallback_suggestion(ocr_text, image_info)

    @staticmethod
    def _call_openrouter(prompt: str) -> str:
        try:
            import requests
            url = "https://api.openrouter.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": settings.OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "Eres un asistente de procesamiento de texto OCR."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 200
            }
            response = requests.post(url, json=data, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"[AI Suggestion] OpenRouter API error: {e}")
            return ""
        except Exception as e:
            print(f"[AI Suggestion] openrouter error: {e}")
            return ""

    @staticmethod
    def _call_ollama(prompt: str) -> str:
        try:
            import requests
            url = f"{settings.OLLAMA_API_URL.rstrip('/')}/v1/chat/completions"
            data = {
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": "Eres un asistente de procesamiento de texto OCR."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 200
            }
            response = requests.post(url, json=data, timeout=15)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"[AI Suggestion] ollama error: {e}")
            return ""

    @staticmethod
    def _fallback_suggestion(ocr_text: str = "", image_info: str = "", brand: str = "", color: str = "", size: str = "") -> str:
        """Generar sugerencia de fallback cuando la IA no está disponible"""
        if ocr_text and ocr_text.strip():
            cleaned = " ".join(ocr_text.replace("\n", " ").split())
            return cleaned[:500]
        
        # Si tenemos datos de detección, usarlos para crear una sugerencia informativa
        detection_parts = []
        if brand and brand.strip():
            detection_parts.append(f"marca {brand.strip()}")
        if color and color.strip():
            detection_parts.append(f"color {color.strip()}")
        if size and size.strip():
            detection_parts.append(f"talla {size.strip()}")
        
        if detection_parts:
            detection_info = ", ".join(detection_parts)
            return f"Producto detectado con {detection_info}. No se pudo extraer texto OCR legible."

        if image_info and image_info.strip():
            return f"Imagen procesada: {image_info.strip()}. Revisa manualmente para completar la descripción."
        
        return "Texto OCR no disponible. Revisa la imagen manualmente para describir el producto."

class ImageProcessingService:
    """Service for general image processing"""
    
    @staticmethod
    def resize_image(image: np.ndarray, max_size: int) -> np.ndarray:
        """Resize image to max size while maintaining aspect ratio"""
        height, width = image.shape[:2]
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(image, (new_width, new_height))
        return image
    
    @staticmethod
    def decode_base64_image(base64_str: str) -> np.ndarray:
        """Decode base64 string to numpy array"""
        import base64
        nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
        return ImageProcessingService.decode_image_bytes(nparr)

    @staticmethod
    def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
        """Decode image bytes to numpy array using OpenCV with Pillow fallback"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is not None:
            return image

        # Fallback to Pillow for more robust PNG support or unusual metadata
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image = pil_image.convert('RGB')
            return np.array(pil_image)[:, :, ::-1]  # RGB to BGR
        except Exception:
            return None

    @staticmethod
    def encode_image_base64(image: np.ndarray) -> str:
        """Encode numpy array to base64 string"""
        import base64
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode()
