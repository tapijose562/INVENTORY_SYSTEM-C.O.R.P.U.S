"""
Script de configuración e instalación del flujo de trabajo completo
1. Descargar dataset de Roboflow
2. Preparar estructura
3. Listar dependencias instaladas
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """Ejecuta un comando y reporta el estado"""
    print(f"\n{'='*60}")
    print(f"▶️ {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error: {e}")
        return False

def setup_workflow():
    """Configura el flujo de trabajo completo"""
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  INVENTORY CORPUS v2 - SETUP WORKFLOW                      ║
║  Descargar Dataset + Preparar Entorno                      ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Paso 1: Verificar estructura
    print("\n📁 Verificando estructura de directorios...")
    dirs = ["datasets", "runs", "training"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {d}/")
    
    # Paso 2: Instalar dependencias
    if not run_command(
        "pip install -r requirements.txt",
        "Instalando dependencias de ml-pipeline"
    ):
        print("⚠️ Error instalando dependencias. Continúa manualmente.")
    
    # Paso 3: Descargar dataset
    if not run_command(
        "python download_dataset.py",
        "Descargando dataset de Roboflow"
    ):
        print("⚠️ Error descargando dataset. Verifica tu API key.")
        return False
    
    # Paso 4: Verificar dataset
    dataset_path = Path("datasets")
    if dataset_path.exists():
        yaml_files = list(dataset_path.glob("**/data.yaml"))
        if yaml_files:
            print(f"\n✅ Dataset descargado en: {dataset_path.absolute()}")
            print(f"   Archivo de configuración: {yaml_files[0]}")
        else:
            print(f"⚠️ Dataset descargado pero no se encontró data.yaml")
    
    # Paso 5: Próximos pasos
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  PRÓXIMOS PASOS                                            ║
╚════════════════════════════════════════════════════════════╝

1. Copiar .env.example a .env y ajustar valores:
   cp .env.example .env

2. Ejecutar entrenamiento:
   python training/train_model.py

3. Para usar el modelo en backend:
   cp runs/detect/*/weights/best.pt ../backend/models/

Documentación:
   - docs/ML_PIPELINE.md
   - ROBOFLOW_SETUP.md

""")
    
    return True

if __name__ == "__main__":
    try:
        success = setup_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
