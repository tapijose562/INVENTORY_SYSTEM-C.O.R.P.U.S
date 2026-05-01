from pathlib import Path
import shutil
import sys
import glob

import argparse
import os
from roboflow import Roboflow

# API key hardcoded for test purposes (as requested)
API_KEY = "sxFgn15NLHMb5G5a0Ae7"


def download_sample_image(version_requested=None):
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace("corpus-jskv8").project("corpus-bodjj")

    # Determinar la versión a usar: argumento > env var > por defecto 5
    if version_requested is None:
        env_v = os.environ.get("ROBOFLOW_VERSION")
        if env_v:
            try:
                version_requested = int(env_v)
            except Exception:
                version_requested = env_v
        else:
            version_requested = 5

    # Intentar la versión pedida; si falla, intentar 'latest' o buscar una versión existente
    version = None
    try:
        version = project.version(version_requested)
        print(f"Usando versión solicitada: {version_requested}")
    except Exception:
        try:
            version = project.version("latest")
            print("Versión solicitada no encontrada; usando 'latest'.")
        except Exception:
            for v in range(50, 0, -1):
                try:
                    version = project.version(v)
                    print(f"Versión solicitada no encontrada; usando versión encontrada: {v}")
                    break
                except Exception:
                    continue
    if version is None:
        print("No se encontró ninguna versión válida del proyecto en Roboflow.")
        sys.exit(1)

    print("Descargando dataset desde Roboflow...")
    ds = version.download("yolov8")

    # ds may be a string path or an object with a .location attribute
    if hasattr(ds, "location"):
        dataset_dir = Path(ds.location)
    else:
        dataset_dir = Path(str(ds))

    if not dataset_dir.exists():
        print(f"Directorio de dataset no encontrado: {dataset_dir}")
        sys.exit(1)

    # Buscar una imagen de prueba dentro deldataset
    img_patterns = ["**/*.jpg", "**/*.jpeg", "**/*.png"]
    found = None
    for pat in img_patterns:
        matches = list(dataset_dir.glob(pat))
        if matches:
            found = matches[0]
            break

    if not found:
        print(f"No se encontró ninguna imagen en {dataset_dir}")
        sys.exit(1)

    dest = Path("test.jpg")
    shutil.copyfile(found, dest)
    print(f"Imagen de prueba copiada: {found} -> {dest}")


if __name__ == "__main__":
    download_sample_image()
