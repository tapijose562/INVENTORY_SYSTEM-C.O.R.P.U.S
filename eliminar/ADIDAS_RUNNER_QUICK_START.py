#!/usr/bin/env python
"""
Guía visual para registrar y entrenar el Adidas Runner
Sin dependencia de APIs complejas
"""

from pathlib import Path
import os

def main():
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🚀 ADIDAS RUNNER - GUÍA COMPLETA DE ENTRENAMIENTO 🚀".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    # Paso 1: Crear carpetas
    print("=" * 70)
    print("📁 PASO 1: PREPARAR CARPETAS PARA IMÁGENES")
    print("=" * 70)
    
    images_dir = Path("assets/images/adidas_runner")
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✅ Carpeta creada: {images_dir.absolute()}\n")

    # Paso 2: Instrucciones para copiar imágenes
    print("=" * 70)
    print("📷 PASO 2: COPIAR IMÁGENES DEL ADIDAS RUNNER")
    print("=" * 70)
    
    print(f"""
📌 INSTRUCCIONES:

1. Tienes 6 imágenes del Adidas Runner (azul marino y blanco)
   que se proporcionaron como referencia.

2. Cópialas a esta carpeta:
   📂 {images_dir.absolute()}

3. Asegúrate que las imágenes sean nombradas así:
   • adidas_runner_001.jpg
   • adidas_runner_002.jpg
   • adidas_runner_003.jpg
   • (etc...)

4. FORMATOS ACEPTADOS:
   ✓ JPG/JPEG
   ✓ PNG
   
5. RECOMENDACIONES:
   ✓ Mínimo 20-30 imágenes para buen entrenamiento
   ✓ Toma más fotos desde:
     - Ángulo frontal
     - Ángulo lateral (45°, 90°)
     - Ángulo trasero
     - Diferentes alturas
     - Bajo diferentes iluminaciones
    """)
    
    # Verificar imágenes
    existing_images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    print(f"📊 Imágenes encontradas: {len(existing_images)}\n")

    # Paso 3: Registrar en el sistema
    print("=" * 70)
    print("✍️  PASO 3: REGISTRAR PRODUCTO EN EL SISTEMA")
    print("=" * 70)
    
    print("""
OPCIÓN A: Vía Frontend (Recomendado)
─────────────────────────────────────
1. Abre el navegador: http://localhost:4200
2. Ve a: 📦 Products
3. Click en: "Create New Product"
4. Ingresa estos datos:

   ┌─────────────────────────────────┐
   │ Nombre: Adidas Runner           │
   │ Marca: Adidas                   │
   │ Colores: Navy Blue / White      │
   │ Talla: 42                       │
   │ Stock: 10                       │
   │ Precio: 125.99 (o 12599 centavos) │
   │ Descripción: Adidas Running Shoe│
   └─────────────────────────────────┘

5. Click: "Create Product"
6. Captura el ID del producto (aparecerá en la respuesta)

OPCIÓN B: Vía Terminal (Avanzado)
──────────────────────────────────
curl -X POST http://localhost:8000/api/v1/products \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Adidas Runner",
    "brand": "Adidas",
    "colors": "Navy Blue / White",
    "color_primary": "Navy Blue",
    "color_secondary": "White",
    "size": "42",
    "stock": 10,
    "price": 12599,
    "color_rgb": {"r": 0, "g": 51, "b": 102},
    "yolo_confidence": 0.85,
    "detection_metadata": {"shoe_type": "running"}
  }'
    """)

    # Paso 4: Subir imágenes
    print("\n" + "=" * 70)
    print("🖼️  PASO 4: SUBIR IMÁGENES AL PRODUCTO")
    print("=" * 70)
    
    print("""
1. En el Frontend, ve a: 📦 Products
2. Busca: "Adidas Runner"
3. Click en el producto
4. Encontrarás la sección: "📷 Upload Images"
5. Sube las imágenes del Adidas Runner:
   • Arrastra 5-30 imágenes
   • O selecciona una carpeta
   
6. El sistema:
   ✅ Validará cada imagen
   ✅ La guardará en el servidor
   ✅ Actualizará la lista de imágenes del producto
    """)

    # Paso 5: Entrenar YOLO
    print("\n" + "=" * 70)
    print("🤖 PASO 5: ENTRENAR EL MODELO YOLO")
    print("=" * 70)
    
    print("""
1. Ve a: 🎓 Training (en el menú)
2. Verás la opción: "Train YOLO Model"
3. El sistema:
   ✅ Detectará las imágenes cargadas del Adidas Runner
   ✅ Creará el dataset de entrenamiento automáticamente
   ✅ Entrenará el modelo durante:
      ⏱️  5-10 minutos (GPU rápida)
      ⏱️  15-30 minutos (sin GPU)
   ✅ Guardará el modelo entrenado
   
4. MONITOREO:
   📊 Verás en tiempo real:
   • Época actual / Total de épocas
   • Pérdida (Loss)
   • Precisión (Precision)
   • Recall
   • mAP50
   
5. Espera hasta que termine
   ✅ Estado: GREEN cuando esté listo
    """)

    # Paso 6: Probar en tiempo real
    print("\n" + "=" * 70)
    print("⚡ PASO 6: DETECTAR EN TIEMPO REAL")
    print("=" * 70)
    
    print("""
1. Ve a: 🔍 Detection
2. Encontrarás: "⚡ Real-Time Detection Mode (Beta)"
3. Click en: "Start Real-Time Detection"
4. Permitir acceso a cámara (cuando lo pida)
5. Presenta el Adidas Runner a la cámara:
   
   📹 POSICIONES RECOMENDADAS:
   ├─ Frontal (vista desde arriba)
   ├─ Lateral izquierda (45°)
   ├─ Lateral derecha (45°)
   ├─ Trasera
   └─ Diferentes ángulos
   
   💡 EL SISTEMA DEBE MOSTRAR:
   ├─ ✅ Brand: "Adidas"
   ├─ ✅ Colors: "Navy Blue / White"
   ├─ ✅ Size: "42"
   ├─ ✅ Confidence: > 0.85
   └─ ✅ Price: "$125.99"

6. MÉTRICAS EN PANTALLA:
   📊 FPS: Fotogramas por segundo
   📊 Detection Time: ms por detección
   📊 Accuracy: Precisión
   📊 History: Últimas detecciones

7. GUARDAR RESULTADOS:
   • Cada detección se registra automáticamente
   • Los datos ayudan a mejorar el modelo
    """)

    # Paso 7: Mejoras iterativas
    print("\n" + "=" * 70)
    print("🔄 PASO 7: MEJORA ITERATIVA (Opcional)")
    print("=" * 70)
    
    print("""
CICLO DE MEJORA:

1️⃣  Recopilar más imágenes:
   • Toma fotos adicionales en diferentes escenarios
   • Diferentes iluminaciones
   • Diferentes ángulos
   • Diferentes fondos

2️⃣  Subir nuevas imágenes:
   • Ve a 📦 Products > Adidas Runner
   • Sube las nuevas imágenes

3️⃣  Re-entrenar:
   • Ve a 🎓 Training
   • El sistema detectará las nuevas imágenes
   • Entrena nuevamente
   • El modelo será actualizado

4️⃣  Probar de nuevo:
   • Ve a 🔍 Detection
   • Verifica que la precisión mejoró

💡 RESULTADO: Con cada iteración, la detección será más precisa
    """)

    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN DEL PROCESO COMPLETO")
    print("=" * 70)
    
    print(f"""
✅ CHECKLIST DE EJECUCIÓN:

☐ 1. Imágenes copiadas a: {images_dir.absolute()}
☐ 2. Producto "Adidas Runner" registrado en el sistema
☐ 3. ID del producto anotado: _______________
☐ 4. Imágenes subidas al producto (5-30 imágenes)
☐ 5. Modelo YOLO entrenado exitosamente
☐ 6. Detección en tiempo real funcionando
☐ 7. Cámara detecta el Adidas Runner con >0.85 precisión

📞 SOPORTE:
   Si tienes problemas:
   • Revisa los logs en: http://localhost:8000/logs
   • Backend debe estar corriendo en puerto 8000
   • Frontend debe estar corriendo en puerto 4200
   • Cámara debe estar disponible en tu dispositivo

🎯 OBJETIVO:
   Cuando des vuelta el Adidas Runner frente a la cámara,
   el sistema lo reconozca automáticamente como:
   
   "Adidas Runner - Navy Blue / White - Talla 42 - $125.99"
   
   CON PRECISIÓN > 85% ✅
    """)

    print("\n" + "="*70)
    print("¡PROCESO INICIADO! Sigue los pasos de arriba →")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
