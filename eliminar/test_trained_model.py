"""
Script de prueba rápida del modelo YOLO entrenado
"""

import os
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from corpus_detector_integration import CorpusDetector

def main():
    print("=" * 60)
    print("🧪 PRUEBA DEL MODELO YOLO ENTRENADO - CORPUS DETECTOR")
    print("=" * 60)
    
    # Ubicación del modelo
    model_path = "backend/corpus_detector.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        print(f"✅ Copiar: ml-pipeline/runs/corpus_final/weights/best.pt -> {model_path}")
        return
    
    print(f"\n📦 Inicializando detector...")
    try:
        detector = CorpusDetector(model_path)
    except Exception as e:
        print(f"❌ Error al cargar modelo: {e}")
        return
    
    # Buscar imagen de prueba
    test_images = [
        "ml-pipeline/corpus-1/valid/images/corpus-1_png.rf.123_jpg.rf.12345.jpg",
        "ml-pipeline/corpus-1/train/images/corpus-1_png.rf.0_jpg.rf.0.jpg",
    ]
    
    found_image = None
    for img_path in test_images:
        if os.path.exists(img_path):
            found_image = img_path
            break
    
    if not found_image:
        print("⚠️ No se encontraron imágenes de prueba")
        print("Dataset disponible en: ml-pipeline/corpus-1/")
        return
    
    print(f"✅ Imagen de prueba: {found_image}")
    
    print(f"\n🔍 Ejecutando detección...")
    try:
        results = detector.detect(found_image, conf=0.3)
        
        print(f"\n✅ Detección completada!")
        print(f"   Confianza mínima: {results['confidence_threshold']}")
        print(f"   Objetos detectados: {len(results['detections'])}")
        
        if results['detections']:
            print(f"\n📊 Resultados:")
            for i, det in enumerate(results['detections'], 1):
                bbox = det['bbox']
                print(f"   {i}. Clase: {det['class']}")
                print(f"      Confianza: {det['confidence']:.2%}")
                print(f"      Caja: ({bbox['x1']:.0f}, {bbox['y1']:.0f}) -> ({bbox['x2']:.0f}, {bbox['y2']:.0f})")
                print(f"      Tamaño: {bbox['width']:.0f}x{bbox['height']:.0f}")
        else:
            print("   ℹ️ No se detectaron objetos con confianza > 30%")
    
    except Exception as e:
        print(f"❌ Error durante detección: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\n📚 Próximos pasos:")
    print("   1. Integrar detector en backend FastAPI")
    print("   2. Ampliar dataset para mejor precisión")
    print("   3. Implementar reentrenamiento continuo")
    print("   4. Desplegar en producción")

if __name__ == "__main__":
    main()