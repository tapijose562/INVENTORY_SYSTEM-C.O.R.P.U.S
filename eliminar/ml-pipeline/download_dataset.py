"""
Script para descargar dataset de Roboflow para YOLO v8
"""
import os
import sys
import shutil
from pathlib import Path
from roboflow import Roboflow

def download_roboflow_dataset(api_key, workspace, project, version, output_dir="datasets"):
    """
    Descarga dataset de Roboflow en formato YOLO v8
    
    Args:
        api_key (str): API key de Roboflow
        workspace (str): Workspace ID
        project (str): Project ID
        version (int): Version number
        output_dir (str): Directorio de salida
    """
    # Crear directorio si no existe
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Descargando dataset de Roboflow...")
    print(f"   Workspace: {workspace}")
    print(f"   Project: {project}")
    print(f"   Version: {version}")
    print(f"   Destino: {output_path.absolute()}")
    
    try:
        # Inicializar Roboflow
        rf = Roboflow(api_key=api_key)
        
        # Obtener proyecto
        project_obj = rf.workspace(workspace).project(project)
        
        # Obtener versión
        dataset_version = project_obj.version(version)
        
        # Descargar en formato YOLO v8
        dataset = dataset_version.download("yolov8", location=str(output_path))
        
        print(f"✅ Dataset descargado exitosamente en: {output_path.absolute()}")
        return dataset
        
    except Exception as e:
        print(f"❌ Error descargando dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configuración (actualiza con tus valores)
    API_KEY = os.getenv("ROBOFLOW_API_KEY", "hJnzXA8i1gDgedcneU6z")
    WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "corpus-e4hp8")
    PROJECT = os.getenv("ROBOFLOW_PROJECT", "corpus-hucc7")
    VERSION = int(os.getenv("ROBOFLOW_VERSION", "1"))
    OUTPUT_DIR = os.getenv("ROBOFLOW_OUTPUT_DIR", "datasets")
    
    # Descargar dataset
    dataset = download_roboflow_dataset(API_KEY, WORKSPACE, PROJECT, VERSION, OUTPUT_DIR)
    
    # Verificar si se descargó en un subdirectorio y mover si es necesario
    downloaded_path = Path(OUTPUT_DIR) / f"{PROJECT}-{VERSION}"
    if downloaded_path.exists():
        print(f"📁 Dataset descargado en subdirectorio: {downloaded_path}")
        print("   Considera usar este directorio para entrenamiento"
    
    print(f"\n🎉 ¡Dataset listo para usar!")
    print(f"   Ubicación: {Path(OUTPUT_DIR).absolute()}")
    print(f"   Clases: {dataset.names if hasattr(dataset, 'names') else 'Ver data.yaml'}")
