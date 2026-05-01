<#
Script para Windows PowerShell:
- activa el venv si existe
- instala dependencias
- descarga una imagen de prueba desde Roboflow
- ejecuta `test_image.py` usando el modelo `yolov8n.pt` incluido
#>

Write-Host "Instalando dependencias (requirements.txt)..."
python -m pip install -r requirements.txt

Write-Host "Descargando imagen de prueba desde Roboflow..."
python .\download_roboflow.py
<#
Write-Host "Ejecutando test de imagen con yolov8n.pt..."
python .\test_image.py --model yolov8n.pt --image test.jpg
#>
Write-Host "Hecho. Si la GUI no está disponible, las imágenes anotadas se guardarán en el directorio actual."
