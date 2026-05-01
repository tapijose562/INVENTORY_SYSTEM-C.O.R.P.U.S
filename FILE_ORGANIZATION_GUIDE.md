# 📁 Estructura Recomendada para Inventory-Corpus-v2

```
Inventory-Corpus-v2/
├── assets/                          # 📂 Archivos estáticos compartidos
│   ├── images/                      # 🖼️  Imágenes de productos para mostrar
│   │   ├── products/                # Producto principal
│   │   │   ├── product_1.jpg
│   │   │   ├── product_2.jpg
│   │   │   └── ...
│   │   └── detections/              # Imágenes de detección temporal
│   │       ├── detect_001.jpg
│   │       └── ...
│   └── models/                      # 🤖 Modelos YOLO entrenados
│       ├── yolov8n.pt
│       └── custom_yolo.pt
│
├── data/                            # 🗃️  Datos de entrenamiento YOLO
│   ├── raw/                         # Datos crudos originales
│   ├── processed/                   # Datos procesados
│   └── annotations/                 # Labels YOLO (.txt)
│       ├── train/
│       ├── val/
│       └── test/
│
├── backend/
│   ├── uploads/                     # 🚫 DEPRECATED - Mover a assets/images/
│   └── ...
│
└── ml-pipeline/
    ├── training/
    │   ├── datasets/                # 🔗 Symlink a ../../data/
    │   └── scripts/
    └── models/                      # 🔗 Symlink a ../../assets/models/
```

## 🎯 **Recomendación: Estructura Unificada**

### **Opción 1: Una sola ruta principal (RECOMENDADA)**
```
assets/
├── images/          # Todas las imágenes (productos + detección)
├── models/          # Modelos YOLO
└── data/           # Datos de entrenamiento
```

### **Opción 2: Separación clara por propósito**
```
images/             # Para mostrar productos en UI
├── products/       # Producto principal (permanente)
└── temp/          # Detección temporal (se puede limpiar)

training/           # Solo para ML training
├── images/         # Dataset de entrenamiento
├── labels/         # Annotations YOLO
└── models/         # Modelos entrenados
```

## 🔄 **Migración Recomendada**

1. **Crear nueva estructura:**
   ```bash
   mkdir -p assets/{images/{products,detections},models}
   mkdir -p data/{raw,processed,annotations/{train,val,test}}
   ```

2. **Mover archivos existentes:**
   ```bash
   # Mover imágenes de productos
   mv backend/uploads/product_*.jpg assets/images/products/

   # Mover imágenes de detección
   mv backend/uploads/detect_*.jpg assets/images/detections/

   # Mover labels
   mv backend/uploads/labels/*.txt data/annotations/train/

   # Mover modelos
   mv models/*.pt assets/models/
   ```

3. **Crear symlinks para compatibilidad:**
   ```bash
   ln -s ../../assets/images backend/uploads
   ln -s ../../data ml-pipeline/training/datasets
   ln -s ../../assets/models ml-pipeline/models
   ```

## ✅ **Beneficios de la Estructura Unificada**

- **🏗️ Arquitectura clara**: Propósito de cada directorio evidente
- **🔄 Reutilización**: Imágenes de productos sirven para UI y training
- **🧹 Mantenimiento**: Fácil limpiar archivos temporales
- **📊 Escalabilidad**: Fácil agregar nuevos tipos de assets
- **🔗 Compatibilidad**: Symlinks mantienen funcionamiento actual