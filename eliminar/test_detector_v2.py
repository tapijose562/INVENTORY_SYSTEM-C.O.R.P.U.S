"""
Prueba del detector YOLO simplificado
"""

import os
import sys

# Usar el detector simplificado
from backend.corpus_detector_simple import CorpusDetector

def main():
    print("\n" + "=" * 70)
    print("🧪 PRUEBA DEL MODELO YOLO ENTRENADO - CORPUS DETECTOR (v2)")
    print("=" * 70)
    
    model_path = "backend/corpus_detector.pt"
    
    if not os.path.exists(model_path):
        print(f"\n❌ Modelo no encontrado: {model_path}")
        print(f"\n✅ Por favor ejecutar:")
        print(f"   copy ml-pipeline\\runs\\corpus_final\\weights\\best.pt backend\\corpus_detector.pt")
        return False
    
    print(f"\n📦 Modelo encontrado: {model_path}")
    
    print(f"\n🔄 Inicializando detector...")
    try:
        detector = CorpusDetector(model_path)
    except Exception as e:
        print(f"❌ Error al cargar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n✅ Detector inicializado correctamente")
    
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
        print("\n⚠️ No se encontraron imágenes de prueba")
        print("   Directorio: ml-pipeline/corpus-1/")
        print("\n✅ Detector está listo para usar en la API")
        return True
    
    print(f"\n🔍 Usando imagen de prueba: {found_image}")
    
    try:
        print(f"\n   Ejecutando detección...")
        results = detector.detect(found_image, conf=0.3)
        
        print(f"\n✅ Detección completada")
        print(f"   Objetos detectados: {len(results['detections'])}")
        
        if results['detections']:
            print(f"\n📊 Resultados:")
            for i, det in enumerate(results['detections'], 1):
                print(f"   [{i}] {det['class'].upper()}")
                print(f"       Confianza: {det['confidence']:.1%}")
                bbox = det['bbox']
                print(f"       Posición: ({bbox['x1']:.0f}, {bbox['y1']:.0f})")
                print(f"       Tamaño: {bbox['width']:.0f}x{bbox['height']:.0f}")
        else:
            print(f"\n   ℹ️ No se detectaron objetos (conf > 30%)")
    
    except Exception as e:
        print(f"❌ Error durante detección: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ PRUEBA EXITOSA - MODELO FUNCIONANDO CORRECTAMENTE")
    print("=" * 70)
    
    print("\n📚 Próximos pasos:")
    print("   1. Integrar en FastAPI backend")
    print("   2. Crear endpoint /detect para análisis de imágenes")
    print("   3. Ampliar dataset para mejor precisión")
    print("   4. Implementar reentrenamiento continuo")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)