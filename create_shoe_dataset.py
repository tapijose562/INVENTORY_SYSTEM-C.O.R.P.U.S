#!/usr/bin/env python
"""
Script para crear dataset básico de zapatos para entrenamiento YOLO
"""

import os
import cv2
import numpy as np
from pathlib import Path
import requests
from PIL import Image
import random

def create_synthetic_shoe_dataset(num_images=50):
    """Crear dataset sintético de zapatos para entrenamiento"""

    dataset_dir = Path("ml-pipeline/training/datasets/shoes_dataset")
    images_dir = dataset_dir / "images"
    labels_dir = dataset_dir / "labels"

    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creando dataset sintético en: {dataset_dir}")

    shoe_templates = [
        {"name": "sneaker", "color": (255, 255, 255), "size": (200, 100)},  # Blanco
        {"name": "boot", "color": (0, 0, 0), "size": (150, 200)},         # Negro
        {"name": "sandal", "color": (139, 69, 19), "size": (180, 80)},    # Marrón
        {"name": "heel", "color": (255, 0, 0), "size": (100, 150)},       # Rojo
    ]

    for i in range(num_images):
        # Crear imagen base
        img = np.random.randint(200, 255, (400, 600, 3), dtype=np.uint8)  # Fondo gris claro

        # Seleccionar template aleatorio
        template = random.choice(shoe_templates)

        # Posición aleatoria
        x = random.randint(50, 400)
        y = random.randint(50, 250)

        # Dibujar "zapato"
        cv2.rectangle(img, (x, y), (x + template["size"][0], y + template["size"][1]),
                     template["color"], -1)

        # Agregar variaciones
        if random.random() > 0.5:
            # Agregar detalles
            cv2.circle(img, (x + 50, y + 50), 20, (0, 0, 0), 2)

        # Guardar imagen
        img_path = images_dir / "04d"
        cv2.imwrite(str(img_path), img)

        # Crear etiqueta YOLO (formato: class x_center y_center width height)
        # Normalizar coordenadas (0-1)
        img_h, img_w = img.shape[:2]
        x_center = (x + template["size"][0]/2) / img_w
        y_center = (y + template["size"][1]/2) / img_h
        width = template["size"][0] / img_w
        height = template["size"][1] / img_h

        label_path = labels_dir / "04d"
        with open(label_path, 'w') as f:
            f.write("0.6f")

    print(f"Dataset creado con {num_images} imágenes")
    print("Para entrenar: cd ml-pipeline && python training/train.py")

def download_shoe_images(num_images=20):
    """Descargar imágenes de zapatos de fuentes públicas"""

    dataset_dir = Path("ml-pipeline/training/datasets/shoes_dataset")
    images_dir = dataset_dir / "images"
    labels_dir = dataset_dir / "labels"

    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    print("Descargando imágenes de zapatos...")

    # URLs de ejemplo (reemplaza con URLs reales de datasets públicos)
    shoe_urls = [
        "https://example.com/shoe1.jpg",  # Reemplaza con URLs reales
        "https://example.com/shoe2.jpg",
    ]

    for i, url in enumerate(shoe_urls[:num_images]):
        try:
            response = requests.get(url, timeout=10)
            img = Image.open(io.BytesIO(response.content))
            img = img.resize((640, 480))

            img_path = images_dir / "04d"
            img.save(img_path)

            # Crear etiqueta básica (bounding box completo)
            label_path = labels_dir / "04d"
            with open(label_path, 'w') as f:
                f.write("0 0.5 0.5 1.0 1.0\n")  # class x_center y_center width height

        except Exception as e:
            print(f"Error descargando {url}: {e}")

    print("Descarga completada")

if __name__ == "__main__":
    print("=== CREADOR DE DATASET DE ZAPATOS ===\n")

    print("1. Creando dataset sintético...")
    create_synthetic_shoe_dataset(100)

    print("\n2. Dataset listo para entrenamiento")
    print("Ejecuta: cd ml-pipeline && python training/train.py")