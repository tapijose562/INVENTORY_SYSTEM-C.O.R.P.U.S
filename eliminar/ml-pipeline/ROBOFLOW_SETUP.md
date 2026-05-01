# 🚀 Roboflow Dataset - Guía de Integración

## Inicio Rápido

### 1. **Preparar Entorno**
```bash
cd ml-pipeline
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. **Configurar Variables de Entorno**
```bash
# Copiar template
cp .env.example .env

# Editar .env con tus valores de Roboflow:
# ROBOFLOW_API_KEY=tu_api_key
# ROBOFLOW_WORKSPACE=tu_workspace
# ROBOFLOW_PROJECT=tu_project
```

### 3. **Descargar Dataset**

**Opción A - Descarga directa:**
```bash
python download_dataset.py
```

**Opción B - Setup completo (recomendado):**
```bash
python setup_workflow.py
```

Este comando:
- ✅ Instala todas las dependencias
- ✅ Descarga el dataset de Roboflow
- ✅ Prepara la estructura de directorios
- ✅ Valida el dataset

---

## Estructura Resultante

```
ml-pipeline/
├── datasets/                    # ← Dataset descargado
│   ├── data.yaml               # Configuración YOLO
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── labels/
│       ├── train/
│       ├── val/
│       └── test/
├── runs/                        # Resultados de entrenamientos
├── training/                    # Scripts de entrenamiento
└── models/                      # Modelos YOLO
```

---

## Entrenar Modelo

Una vez que tengas el dataset:

```bash
python training/train_model.py
```

O si tienes el script de entrenamiento personalizado:

```bash
python train_yolo_clean.py
```

---

## Integración con Backend

Después del entrenamiento, copiar el modelo al backend:

```bash
cp runs/detect/*/weights/best.pt ../backend/models/corpus_v1.pt
```

Luego actualizar en [backend/app/config.py](../backend/app/config.py):
```python
MODEL_PATH = "models/corpus_v1.pt"
```

---

## Solución de Problemas

### ❌ "API key inválida"
- Verificar que `ROBOFLOW_API_KEY` en `.env` sea correcto
- Regenerar key en dashboard de Roboflow

### ❌ "Workspace/Project no encontrado"
- Verificar valores en Roboflow dashboard
- Asegurar que la versión existe

### ❌ Error descargando
```bash
# Limpiar caché y reintentar
rm -rf datasets
python download_dataset.py
```

---

## Automatizar Descargas Periódicas

Para actualizar automáticamente el dataset (ej: diariamente):

**Windows - Task Scheduler:**
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\ml-pipeline\download_dataset.py"
Register-ScheduledTask -TaskName "Roboflow-Dataset-Update" -Trigger $trigger -Action $action
```

**Linux/Mac - Cron:**
```bash
0 2 * * * cd /path/to/ml-pipeline && python download_dataset.py
```

---

## Referencias

- 📚 [Roboflow Documentation](https://docs.roboflow.com/)
- 📚 [YOLOv8 Documentation](https://docs.ultralytics.com/)
- 📚 [Pipeline ML Docs](../docs/ML_PIPELINE.md)
