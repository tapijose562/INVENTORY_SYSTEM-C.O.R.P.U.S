# CUDA Setup Guide - GPU Acceleration

## ¿Qué es CUDA?

CUDA es la plataforma de NVIDIA para computación paralela en GPU. Es **opcional** pero **muy recomendado** para acelerar:
- Inferencia YOLO (5-10x más rápido)
- Entrenamiento de modelos (10-50x más rápido)
- Procesamiento de imágenes

**Sin GPU:** ~500ms por imagen
**Con GPU:** ~50ms por imagen

---

## Requisitos

✓ GPU NVIDIA (RTX series, GTX 1060+, Tesla, etc.)
✓ Driver NVIDIA actualizado
✓ CUDA Toolkit
✓ cuDNN

---

## Instalación

### 1️⃣ Verificar GPU

```bash
# Windows PowerShell
nvidia-smi

# Debe mostrar:
# - GPU Name (ej: NVIDIA GeForce RTX 3080)
# - CUDA Version (ej: 12.1)
```

Si no aparece nada, actualizar drivers: https://www.nvidia.com/Download/driverDetails.aspx

### 2️⃣ Instalar CUDA Toolkit

**Descargar:** https://developer.nvidia.com/cuda-downloads

Ejemplos:
- **CUDA 12.1** para RTX 3000/4000 series
- **CUDA 11.8** para RTX 2000 series
- **CUDA 11.0** para GTX 1000 series

**Windows:**
```bash
# Descargar .exe
# Ejecutar instalador
# Seleccionar: CUDA Development + cuDNN
# Ruta: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1
```

**Linux:**
```bash
# Ubuntu 22.04
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.1-530.30.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.1-530.30.02-1_amd64.deb
sudo apt-get update
sudo apt-get -y install cuda
```

### 3️⃣ Instalar cuDNN

**Descargar:** https://developer.nvidia.com/cudnn (requiere cuenta NVIDIA)

**Windows:**
- Descargar cudnn-windows-x86_64-v8.x.x.zip
- Extraer en: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\`

**Linux:**
```bash
tar -xzvf cudnn-linux-x86_64-8.x.x_cuda12-archive.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h
```

### 4️⃣ Verificar Instalación

```bash
# Windows
nvcc --version

# Linux
/usr/local/cuda/bin/nvcc --version
```

---

## Configurar Python para GPU

### Opción A: PyTorch + CUDA

```bash
cd backend

# Desinstalar versión sin GPU
pip uninstall torch -y

# Instalar con soporte CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verificar
python -c "import torch; print(torch.cuda.is_available())"  # Debe mostrar: True
```

### Opción B: TensorFlow + CUDA

```bash
# Instalar TensorFlow con GPU
pip install tensorflow[and-cuda]==2.14.0

# Verificar
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Opción C: Ultralytics YOLO (Recomendado para nuestro proyecto)

```bash
pip install ultralytics

# Verificar GPU
python -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
print('GPU Available:', model.device)
"
```

---

## Configurar Backend para GPU

### En `backend/.env`:

```env
# GPU Configuration
USE_GPU=True
CUDA_VISIBLE_DEVICES=0  # Si tienes múltiples GPUs, 0=primera GPU

# YOLO
YOLO_DEVICE=0  # 0 para GPU, "cpu" para CPU
```

### En `backend/app/services/ai.py`:

```python
import torch
from ultralytics import YOLO
from app.core.config import settings

class YOLODetectionService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            # Usar GPU si está disponible
            device = 0 if torch.cuda.is_available() else 'cpu'
            self.model = YOLO(settings.YOLO_MODEL_PATH)
            self.model.to(device)
            print(f"✓ YOLO loaded on device: {device}")
        except Exception as e:
            print(f"Error loading YOLO: {e}")
            self.model = YOLO("yolov8n.pt")
```

---

## Pruebas de Velocidad

### Benchmark YOLO

```python
import time
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
image = cv2.imread("shoe.jpg")

# Sin GPU
model.to('cpu')
start = time.time()
results = model.predict(image)
cpu_time = time.time() - start
print(f"CPU: {cpu_time*1000:.2f}ms")

# Con GPU
model.to(0)  # Primera GPU
start = time.time()
results = model.predict(image)
gpu_time = time.time() - start
print(f"GPU: {gpu_time*1000:.2f}ms")
print(f"Speedup: {cpu_time/gpu_time:.1f}x")
```

### Resultado Esperado

```
CPU: 450ms
GPU: 50ms
Speedup: 9.0x
```

---

## Troubleshooting

### ❌ "CUDA Runtime Error: all CUDA compute capabilities are insufficient"

**Solución:** GPU demasiado antigua. Usar CPU o actualizar GPU.

### ❌ "CUDA out of memory"

**Solución:** Reducir tamaño de imagen o batch size

```python
# Reducir tamaño
model.predict(image, imgsz=320)  # Default: 640

# Reducir batch size en training
trainer.train(batch=4)  # Default: 16
```

### ❌ "Cannot find CUDA toolkit"

```bash
# Verificar variable de entorno
echo %CUDA_PATH%  # Windows
echo $CUDA_PATH  # Linux

# Si no existe, configurar:
setx CUDA_PATH "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1"
```

---

## Comparativa Rendimiento

| Operación | CPU | GPU RTX 3080 | Mejora |
|-----------|-----|--------------|--------|
| Detección 640x640 | 450ms | 45ms | 10x |
| Entrenamiento (100 imgs) | 5min | 30seg | 10x |
| Extracción color | 50ms | 5ms | 10x |
| OCR preprocessing | 100ms | N/A | - |

---

## Próximos Pasos

✅ CUDA instalado y funcional  
→ Configurar backend  
→ Medir velocidad  
→ Optimizar parámetros
