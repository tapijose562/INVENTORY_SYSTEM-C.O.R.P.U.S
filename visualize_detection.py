#!/usr/bin/env python3
"""
VISUALIZADOR DE RESULTADOS DE DETECCIÓN YOLO
Muestra la imagen con las detecciones superpuestas
"""

import cv2
import numpy as np
import os
import json
from pathlib import Path

def draw_detection_box(image, bbox, label, confidence, color_rgb):
    """Dibuja una caja de detección en la imagen con debugging"""
    x1, y1, x2, y2 = map(int, bbox)

    print(f"   📦 Dibujando bounding box: [{x1}, {y1}, {x2}, {y2}]")

    # Validar coordenadas
    height, width = image.shape[:2]
    x1 = max(0, min(x1, width-1))
    y1 = max(0, min(y1, height-1))
    x2 = max(0, min(x2, width-1))
    y2 = max(0, min(y2, height-1))

    print(f"   📦 Coordenadas ajustadas: [{x1}, {y1}, {x2}, {y2}]")

    # Color del rectángulo (rojo brillante para que sea visible)
    box_color = (0, 0, 255)  # Rojo BGR para máxima visibilidad
    print(f"   🎨 Color del rectángulo: {box_color}")

    # Dibujar rectángulo grueso
    thickness = 5  # Más grueso para que sea visible
    cv2.rectangle(image, (x1, y1), (x2, y2), box_color, thickness)
    print("   ✅ Rectángulo dibujado")

    # Texto con etiqueta y confianza
    text = f"{label} ({confidence:.1%})"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2  # Más grande
    thickness = 3

    # Calcular tamaño del texto para el fondo
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Dibujar fondo del texto (negro)
    cv2.rectangle(image, (x1, y1 - text_height - 15), (x1 + text_width + 10, y1), (0, 0, 0), -1)

    # Dibujar texto blanco
    cv2.putText(image, text, (x1 + 5, y1 - 8), font, font_scale, (255, 255, 255), thickness)
    print("   ✅ Texto dibujado")

    return image

def visualize_detection():
    """Visualiza la detección de la imagen específica"""

    # Ruta de la imagen
    image_path = "backend/assets/images/detect_805679660447410c9fd58b97ed2838c1.jpg"

    if not os.path.exists(image_path):
        print(f"❌ Imagen no encontrada: {image_path}")
        return

    # Cargar imagen
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Error al cargar imagen: {image_path}")
        return

    print("\n🖼️  CARGANDO IMAGEN DETECTADA...")
    print(f"   Ruta: {image_path}")
    print(f"   Dimensiones: {image.shape[1]}x{image.shape[0]} píxeles")

    # Datos de detección (de la base de datos)
    detection_data = {
        'bbox': [288.6127014160156, 98.22217559814453, 509.07635498046875, 710.8451538085938],
        'label': 'potential_shoe_skateboard',
        'confidence': 0.593691349029541,
        'color_rgb': {'r': 16, 'g': 23, 'b': 41},
        'colors': ['black', 'blue', 'white'],
        'size': '38'
    }

    # Dibujar la detección
    image_with_detection = draw_detection_box(
        image.copy(),
        detection_data['bbox'],
        detection_data['label'],
        detection_data['confidence'],
        detection_data['color_rgb']
    )

    # Información adicional en la imagen
    info_text = [
        f"Marca: {detection_data['label']}",
        f"Confianza: {detection_data['confidence']:.1%}",
        f"Colores: {', '.join(detection_data['colors'])}",
        f"Tamaño: {detection_data['size']}",
        f"RGB: ({detection_data['color_rgb']['r']}, {detection_data['color_rgb']['g']}, {detection_data['color_rgb']['b']})"
    ]

    # Dibujar información en la esquina superior izquierda
    y_offset = 30
    for line in info_text:
        cv2.putText(image_with_detection, line, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image_with_detection, line, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        y_offset += 30

    # Guardar imagen con detecciones
    output_path = "detection_result_visualized.jpg"
    cv2.imwrite(output_path, image_with_detection)

    print("\n✅ VISUALIZACIÓN COMPLETADA:")
    print(f"   📁 Imagen original: {image_path}")
    print(f"   🎨 Imagen con detección: {output_path}")
    print(f"   📏 Bounding Box: {detection_data['bbox']}")
    print(f"   🎯 Confianza: {detection_data['confidence']:.1%}")
    print(f"   🏷️  Etiqueta: {detection_data['label']}")
    print(f"   🎨 Colores detectados: {', '.join(detection_data['colors'])}")
    print(f"   📏 Tamaño detectado: {detection_data['size']}")

    # Mostrar estadísticas de la detección
    bbox = detection_data['bbox']
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    area = width * height

    print("\n📊 ESTADÍSTICAS DE DETECCIÓN:")
    print(f"   📐 Ancho del objeto: {width:.0f} píxeles")
    print(f"   📐 Alto del objeto: {height:.0f} píxeles")
    print(f"   📐 Área del objeto: {area:.0f} píxeles²")
    print(f"   📍 Centro: ({(bbox[0] + bbox[2])/2:.0f}, {(bbox[1] + bbox[3])/2:.0f})")

    print("\n💡 INTERPRETACIÓN:")
    if detection_data['confidence'] > 0.5:
        print("   ✅ Detección confiable (>50%)")
    else:
        print("   ⚠️  Detección de baja confianza (<50%)")

    if 'shoe' in detection_data['label'].lower():
        print("   👟 Objeto identificado como calzado")
    else:
        print("   ❓ Objeto identificado como potencial calzado/deporte")

    print("\n🔍 PARA VER LA IMAGEN:")
    print(f"   • Abre el archivo: {output_path}")
    print("   • O ejecuta: start detection_result_visualized.jpg")
    return image_with_detection

if __name__ == "__main__":
    visualize_detection()