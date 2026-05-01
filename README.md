# YOLOv8 CPU - Quick Start

## Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

Si quieres instalar directo:

```powershell
python -m pip install ultralytics opencv-python roboflow
```

## Descargar dataset desde Roboflow

```powershell
python .\download_dataset.py
```

## Entrenar modelo

Usa el archivo `data.yaml` descargado por Roboflow:

```powershell
python .\train_cpu.py
```

Al terminar, el modelo entrenado normalmente queda en una ruta parecida a:

```text
runs\detect\train\weights\best.pt
```

Copia ese `best.pt` a esta carpeta con el nombre `best.pt`.

## Probar con imagen

```powershell
.\run_image_test.ps1
```

Solo deja en esta carpeta:

- `best.pt`
- `test.jpg`

Si prefieres ejecutar manualmente:

```powershell
python .\test_image.py
```

## Probar con cámara

```powershell
python .\test_camera.py --model .\best.pt --camera 0
```

Presiona `q` para cerrar la ventana de cámara.

## Optimización para CPU

- Usa `yolov8n.pt` o un modelo pequeño.
- Mantén `imgsz=640` o baja a `512`/`416` si quieres más velocidad.
- Entrena y prueba con `device=cpu`.
- En CPU, `workers=0` evita problemas comunes en Windows.
- Si el video va lento, sube `conf` o baja `imgsz`.

## Advertencia / No modificar

- Este repositorio ya está configurado y probado para descargar el dataset, entrenar y ejecutar inferencia.
- NO modifiques los scripts principales (`download_roboflow.py`, `train_cpu.py`, `test_image.py`, `test_camera.py`) si no sabes exactamente qué cambios haces.
- Si vas a cambiar algo, crea primero una copia de seguridad (por ejemplo renombra la carpeta o copia los archivos) para poder volver atrás.
- El flujo recomendado:
	1. Ejecutar `.
un_tests.ps1` para descargar una imagen de prueba y verificar inferencia.
	2. Ejecutar `.
un_train.ps1 -epochs 100` para entrenar (ajusta `-epochs` según tu tiempo/recursos).
	3. Probar con `python .\test_image.py --model runs\detect\train\weights\best.pt --image test.jpg`.

- Si no hay GUI, los scripts guardan imágenes anotadas como `annotated_output.jpg` o `annotated_camera_*.jpg`.

Si quieres que haga un cambio específico o añada control de versiones, dímelo antes de editar los scripts.
