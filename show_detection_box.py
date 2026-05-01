#!/usr/bin/env python3
"""
🎯 VISUALIZADOR DE DETECCIÓN YOLO - VERSIÓN MEJORADA
Crea una imagen clara con el rectángulo de detección visible
"""

import cv2
import numpy as np
import os
import sys

def create_visual_detection():
    """Crea visualización clara de la detección"""

    # Ruta de la imagen
    image_path = "backend/assets/images/detect_805679660447410c9fd58b97ed2838c1.jpg"

    print("\n" + "=" * 70)
    print("🎯 VISUALIZADOR DE DETECCIÓN YOLO - VERSIÓN CLARA")
    print("=" * 70)

    print(f"\n📂 Buscando imagen: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Imagen no encontrada en {image_path}")
        return False

    # Cargar imagen
    print("📖 Cargando imagen...")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ ERROR: No se pudo cargar la imagen")
        return False

    height, width = image.shape[:2]
    print(f"✅ Imagen cargada: {width}x{height} píxeles")

    # DATOS DE DETECCIÓN YOLO
    print("\n📊 DATOS DE DETECCIÓN RECUPERADOS DE BASE DE DATOS:")
    
    bbox = [288.6127014160156, 98.22217559814453, 509.07635498046875, 710.8451538085938]
    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    
    print(f"   • Bounding Box (original): {bbox}")
    print(f"   • Bounding Box (enteros): [{x1}, {y1}, {x2}, {y2}]")
    print(f"   • Objeto: potential_shoe_skateboard")
    print(f"   • Confianza: 59.4%")
    print(f"   • Colores: Negro, Azul, Blanco")

    # Crear copia para dibujar
    image_annotated = image.copy()

    # ✅ PASO 1: DIBUJAR RECTÁNGULO PRINCIPAL (ROJO BRILLANTE)
    print("\n✏️ Dibujando anotaciones...")
    
    # Rectángulo principal en ROJO puro
    cv2.rectangle(image_annotated, (x1, y1), (x2, y2), (0, 0, 255), 8)
    print(f"   ✅ Rectángulo ROJO: [{x1}, {y1}] a [{x2}, {y2}]")

    # ✅ PASO 2: LÍNEAS DE ESQUINA (AMARILLO)
    corner_size = 50
    thickness = 4
    
    # Esquina superior izquierda
    cv2.line(image_annotated, (x1, y1), (x1 + corner_size, y1), (0, 255, 255), thickness)
    cv2.line(image_annotated, (x1, y1), (x1, y1 + corner_size), (0, 255, 255), thickness)
    
    # Esquina superior derecha
    cv2.line(image_annotated, (x2, y1), (x2 - corner_size, y1), (0, 255, 255), thickness)
    cv2.line(image_annotated, (x2, y1), (x2, y1 + corner_size), (0, 255, 255), thickness)
    
    # Esquina inferior izquierda
    cv2.line(image_annotated, (x1, y2), (x1 + corner_size, y2), (0, 255, 255), thickness)
    cv2.line(image_annotated, (x1, y2), (x1, y2 - corner_size), (0, 255, 255), thickness)
    
    # Esquina inferior derecha
    cv2.line(image_annotated, (x2, y2), (x2 - corner_size, y2), (0, 255, 255), thickness)
    cv2.line(image_annotated, (x2, y2), (x2, y2 - corner_size), (0, 255, 255), thickness)
    
    print(f"   ✅ Líneas de esquina AMARILLAS dibujadas")

    # ✅ PASO 3: ETIQUETA EN LA PARTE SUPERIOR
    label_text = "DETECTADO: Shoe/Skateboard (59.4%)"
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 1.5
    font_thickness = 2
    
    # Obtener tamaño de texto
    (text_width, text_height), baseline = cv2.getTextSize(
        label_text, font, font_scale, font_thickness
    )
    
    # Fondo negro para el texto
    label_y = max(text_height + 10, y1 - 10)
    cv2.rectangle(image_annotated,
                 (x1 - 5, label_y - text_height - 10),
                 (x1 + text_width + 5, label_y),
                 (0, 0, 0), -1)
    
    # Texto blanco
    cv2.putText(image_annotated, label_text,
               (x1, label_y - 5),
               font, font_scale, (255, 255, 255), font_thickness)
    
    print(f"   ✅ Etiqueta de texto dibujada")

    # ✅ PASO 4: INFORMACIÓN EN ESQUINA
    info_lines = [
        f"Ancho: {x2 - x1:.0f} px",
        f"Alto: {y2 - y1:.0f} px",
        f"Area: {(x2-x1)*(y2-y1):.0f} px2",
        f"Centro: ({(x1+x2)//2}, {(y1+y2)//2})",
        f"Colores: Negro, Azul, Blanco"
    ]
    
    y_offset = 40
    for info in info_lines:
        cv2.putText(image_annotated, info, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        y_offset += 25
    
    print(f"   ✅ Información adicional dibujada")

    # ✅ PASO 5: CÍRCULO EN EL CENTRO
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    cv2.circle(image_annotated, (center_x, center_y), 15, (0, 255, 255), 3)
    cv2.circle(image_annotated, (center_x, center_y), 3, (0, 255, 255), -1)
    print(f"   ✅ Marcador de centro dibujado en ({center_x}, {center_y})")

    # ✅ GUARDAR RESULTADO
    print("\n💾 Guardando imágenes...")
    
    output_paths = []
    
    # Imagen con anotaciones
    output1 = "detection_YOLO_annotated.jpg"
    if cv2.imwrite(output1, image_annotated):
        file_size = os.path.getsize(output1)
        print(f"   ✅ {output1} ({file_size} bytes)")
        output_paths.append(output1)
    
    # Imagen con más contraste
    image_contrast = image_annotated.copy()
    alpha = 1.3
    beta = 20
    image_contrast = cv2.convertScaleAbs(image_contrast, alpha=alpha, beta=beta)
    
    output2 = "detection_YOLO_high_contrast.jpg"
    if cv2.imwrite(output2, image_contrast):
        file_size = os.path.getsize(output2)
        print(f"   ✅ {output2} ({file_size} bytes)")
        output_paths.append(output2)

    # Imagen recortada (zoom en detección)
    margin = 50
    crop_x1 = max(0, x1 - margin)
    crop_y1 = max(0, y1 - margin)
    crop_x2 = min(width, x2 + margin)
    crop_y2 = min(height, y2 + margin)
    
    image_cropped = image_annotated[crop_y1:crop_y2, crop_x1:crop_x2].copy()
    
    output3 = "detection_YOLO_zoomed.jpg"
    if cv2.imwrite(output3, image_cropped):
        file_size = os.path.getsize(output3)
        print(f"   ✅ {output3} ({file_size} bytes) - Zoom en la detección")
        output_paths.append(output3)

    print("\n" + "=" * 70)
    print("✅ VISUALIZACIÓN COMPLETADA CON ÉXITO")
    print("=" * 70)

    print(f"\n📊 RESUMEN DE DETECCIÓN:")
    print(f"   • Objeto: potential_shoe_skateboard")
    print(f"   • Confianza: 59.4% ✅")
    print(f"   • Colores: Negro (RGB: 16,23,41), Azul, Blanco")
    print(f"   • Tamaño detectado: 38")
    print(f"   • Ubicación: [{x1}, {y1}, {x2}, {y2}]")
    print(f"   • Dimensiones: {x2-x1}x{y2-y1} píxeles")

    print(f"\n📁 IMÁGENES GENERADAS:")
    for i, path in enumerate(output_paths, 1):
        print(f"   {i}. {path}")

    print(f"\n🔍 PARA VER LAS IMÁGENES:")
    print(f"   • Opción 1: explorer . (y hace doble clic en el archivo)")
    print(f"   • Opción 2: start {output_paths[0]}")
    print(f"   • Opción 3: Verlas en VS Code")

    print("\n💡 CARACTERÍSTICAS DE VISUALIZACIÓN:")
    print(f"   ✓ Rectángulo ROJO grueso alrededor del objeto")
    print(f"   ✓ Líneas AMARILLAS en las esquinas")
    print(f"   ✓ Etiqueta con confianza")
    print(f"   ✓ Información técnica")
    print(f"   ✓ Marcador de centro")
    print(f"   ✓ Versión con alto contraste")
    print(f"   ✓ Versión ampliada (zoom)")

    return True

if __name__ == "__main__":
    try:
        success = create_visual_detection()
        if success:
            print("\n🎉 ¡LISTO! Abre las imágenes generadas para ver la detección\n")
        else:
            print("\n❌ Error en la visualización\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
