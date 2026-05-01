<#
PowerShell helper to install deps, download dataset from Roboflow and run training on CPU.
Use with an activated venv for best results.
#>
param(
	[int]$epochs = 100,
	[int]$imgsz = 640
)

Write-Host "Instalando dependencias (requirements.txt)..."
python -m pip install -r requirements.txt

Write-Host "Descargando dataset desde Roboflow..."
python .\download_roboflow.py

Write-Host "Lanzando entrenamiento (CPU) con $epochs epochs y tamaño de imagen $imgsz..."
python .\train_cpu.py --model yolov8n.pt --epochs $epochs --imgsz $imgsz

Write-Host "Entrenamiento iniciado. Revisa la carpeta 'runs' para checkpoints y logs."

Write-Host "Consejo: si el dataset es pequeño, 50-100 epochs suele ser razonable; para datasets grandes sube más. Ajusta '--imgsz' y usa GPU si está disponible para acelerar."
