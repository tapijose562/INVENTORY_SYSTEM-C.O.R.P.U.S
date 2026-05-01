# 🎥 Real-Time Detection - Roboflow Integration Guide

## 📋 Overview

El sistema de **Real-Time Detection** ahora usa un modelo dedicado de Roboflow que detecta **SOLO ZAPATOS** en la cámara en vivo.

### ✅ Separación de Modos de Detección

```
┌─────────────────────────────────────────────┐
│        DETECTION MODES (MODO INDEPENDIENTE) │
├─────────────────────────────────────────────┤
│ 🎥 Real-Time Detection (Cámara en Vivo)     │
│    → Usa: Roboflow Model                    │
│    → Detecta: SOLO ZAPATOS                  │
│    → WebSocket: /api/v1/detection/ws/...    │
├─────────────────────────────────────────────┤
│ 📸 Detection Results (Imágenes Subidas)     │
│    → Usa: YOLO Service (sin cambios)        │
│    → Detecta: Todos los objetos             │
│    → Endpoint: /api/v1/detection/detect...  │
├─────────────────────────────────────────────┤
│ 🎬 Webcam Detection (Otro modo)             │
│    → Usa: YOLO Service (sin cambios)        │
│    → Detecta: Todos los objetos             │
│    → Endpoint: /api/v1/detection/detect...  │
└─────────────────────────────────────────────┘
```

## 🚀 Cómo Usar Tu Modelo de Roboflow

### Opción 1: Usar un Modelo Existente de Roboflow

Si ya tienes un modelo entrenado en Roboflow:

1. **Descarga el modelo** desde `app.roboflow.com`
2. **Exporta como YOLOv8**
3. **Coloca el archivo** en:
   ```
   backend/models/roboflow_shoes.pt
   ```

### Opción 2: Entrenar en Roboflow

1. Ve a [Roboflow.com](https://roboflow.com)
2. Carga tus imágenes de zapatos/calzados
3. Etiqueta las imágenes (bounding boxes alrededor de los zapatos)
4. Genera el dataset
5. Entrena con YOLOv8
6. Descarga el modelo `.pt`
7. Colócalo en `backend/models/roboflow_shoes.pt`

## 📊 Qué Detecta Real-Time Mode

### ✅ EN TIEMPO REAL (Roboflow):
```json
{
  "detections": [
    {
      "id": 1,
      "class": "shoe",
      "confidence": 0.92,
      "bbox": [x1, y1, x2, y2],
      "color": "Black",
      "rgb": {"r": 0, "g": 0, "b": 0},
      "detected_size": "42",
      "product_brand": "Adidas",
      "processing_time": 0.045
    }
  ],
  "shoe_count": 1,
  "mode": "realtime-shoes-only",
  "status": "✅ Shoes detected"
}
```

### ❌ NO detecta en Real-Time:
- Personas
- Mesas
- Cajas
- Fondos
- Cualquier cosa que no sea un zapato

## 🔧 Configuración del Servicio

### Archivo: `backend/app/services/roboflow_detector.py`

```python
# Configurar clases de zapatos reconocidas
shoe_classes = ['shoe', 'shoes', 'sneaker', 'sneakers']

# Umbral de confianza mínima
confidence_threshold = 0.5

# Optimizaciones de tiempo real
imgsz = 416  # Tamaño de imagen (más pequeño = más rápido)
max_det = 5  # Máximo de detecciones
```

### Parámetros Ajustables

En `main.py`, línea con `roboflow_detector.detect_shoes_only()`:

```python
# Aumentar confianza (menos falsos positivos, pero menos sensible)
roboflow_detector.detect_shoes_only(image, confidence_threshold=0.7)

# Disminuir confianza (más sensible, pero más falsos positivos)
roboflow_detector.detect_shoes_only(image, confidence_threshold=0.3)
```

## 🎯 Cómo Cambia la Experiencia del Usuario

### Antes (YOLO General)
```
Cámara muestra:
✅ Zapato detectado
✅ Persona detectada (problema!)
✅ Mesa detectada (problema!)
❌ Mucho ruido, muchos falsos positivos
```

### Después (Roboflow Especializado)
```
Cámara muestra:
✅ Zapato detectado
❌ Persona ignorada
❌ Mesa ignorada
✅ Limpio, solo zapatos relevantes
```

## 📱 Frontend Integration

El Frontend recibe datos con formato `"mode": "realtime-shoes-only"`, permitiendo:

```typescript
if (data.mode === 'realtime-shoes-only') {
  // Mostrar solo detecciones de zapatos
  this.renderShoeDetections(data.detections);
} else {
  // Otros modos de detección
}
```

## 🔍 Flujo de Ejecución

```
Frontend (Webcam)
    ↓
Frame (base64)
    ↓
WebSocket /api/v1/detection/ws/real-time-detection
    ↓
RoboflowShoeDetector.detect_shoes_only()
    ↓
Filtra: ¿Es zapato? SÍ → Procesa
                    NO  → Descarta
    ↓
ColorService.extract_multiple_colors() (del area del zapato)
    ↓
OCRService.extract_text() (talla, marca, etc.)
    ↓
Database lookup (busca producto similar)
    ↓
JSON Response
    ↓
Frontend (Renderiza solo zapatos)
```

## 📋 Archivos Modificados

```
backend/
├── main.py (ACTUALIZADO)
│   ├── Importa: RoboflowShoeDetector
│   ├── Inicializa: roboflow_detector
│   └── WebSocket: Usa detector de Roboflow
│
├── app/services/
│   ├── roboflow_detector.py (NUEVO)
│   │   ├── RoboflowShoeDetector class
│   │   ├── detect_shoes_only()
│   │   └── is_shoe_class()
│   │
│   └── ai.py (SIN CAMBIOS)
│       └── YOLODetectionService (para otros modos)
```

## ✨ Ventajas

1. **Precisión**: Solo detecta zapatos (menos falsos positivos)
2. **Rendimiento**: Modelo optimizado para tiempo real
3. **Aislamiento**: No afecta otros modos de detección
4. **Escalabilidad**: Fácil agregar más modelos especializados
5. **Mantenimiento**: Código separado y modular

## 🚨 Troubleshooting

### "No shoes detected" constantemente
- Aumentar `confidence_threshold` a 0.3-0.4
- Verificar iluminación de la cámara
- Entrenar mejor modelo en Roboflow

### Modelo no carga
- Verificar que el archivo existe en `backend/models/roboflow_shoes.pt`
- Si no existe, usa el fallback automático (YOLO nano)

### Lento en tiempo real
- Reducir `imgsz` de 416 a 320
- Aumentar `confidence_threshold`
- Usar GPU si disponible

## 📚 Referencias

- [Roboflow Documentation](https://docs.roboflow.com/)
- [YOLO v8 Guide](https://docs.ultralytics.com/tasks/detect/)
- [WebSocket FastAPI](https://fastapi.tiangolo.com/advanced/websockets/)

---

**Estado**: ✅ Implementado y Funcionando
**Última actualización**: Abril 2026
