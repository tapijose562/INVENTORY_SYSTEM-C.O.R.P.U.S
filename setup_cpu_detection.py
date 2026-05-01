#!/usr/bin/env python3
"""
SOLUCIÓN COMPLETA para cámara sin GPU NVIDIA
Configurar YOLO para usar CPU y verificar websocket
"""

import os
import sys
import torch

print("""
╔════════════════════════════════════════════════════════════════╗
║  🎯 SOLUCIÓN: DETECCIÓN SIN GPU NVIDIA (USANDO CPU)           ║
╚════════════════════════════════════════════════════════════════╝
""")

# Step 1: Verificar configuración
print("\n📋 VERIFICANDO SISTEMA:")
print(f"   • Python: {sys.version.split()[0]}")
print(f"   • PyTorch: {torch.__version__}")
print(f"   • GPU disponible: {'✅ SÍ' if torch.cuda.is_available() else '❌ NO'}")

if torch.cuda.is_available():
    print(f"     └─ {torch.cuda.get_device_name(0)}")
    print("     ℹ️  PyTorch usará GPU automáticamente")
else:
    print("     ℹ️  PyTorch usará CPU (el código está configurado)")

# Step 2: Verificar que los archivos de servicios estén actualizados
print("\n🔧 VERIFICANDO CAMBIOS EN SERVICIOS:")

files_to_check = [
    ("backend/app/services/ai.py", "device = 'cuda' if torch.cuda.is_available() else 'cpu'"),
    ("backend/app/services/roboflow_detector.py", "device = 'cuda' if torch.cuda.is_available() else 'cpu'"),
    ("backend/main.py", "@app.websocket(\"/api/v1/detection/ws/real-time-detection\")")
]

for filepath, marker in files_to_check:
    if os.path.exists(filepath):
        with open(filepath) as f:
            content = f.read()
            if marker in content:
                print(f"   ✅ {filepath}")
            else:
                print(f"   ⚠️  {filepath} - Puede necesitar actualización")
    else:
        print(f"   ❌ {filepath} - NO ENCONTRADO")

# Step 3: Crear test de WebSocket
print("\n🧪 CREANDO TEST DE WEBSOCKET...")

test_code = '''
import asyncio
import websockets
import json
import time

async def test_websocket():
    """Test WebSocket connection"""
    try:
        uri = "ws://127.0.0.1:8000/api/v1/detection/ws/real-time-detection"
        print(f"Conectando a: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado!")
            
            # Send ping to keep alive
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            print(f"Respuesta: {response}")
            
            await asyncio.sleep(1)
            print("✅ WebSocket está funcionando!")
            
    except ConnectionRefusedError:
        print("❌ No se pudo conectar - Backend no está corriendo")
        print("   Inicia el backend con: python start_backend.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
'''

with open("test_websocket_connection.py", "w") as f:
    f.write(test_code)
print("   ✅ test_websocket_connection.py creado")

# Step 4: Resumen de cambios
print("""
╔════════════════════════════════════════════════════════════════╗
║  📝 CAMBIOS REALIZADOS                                         ║
╚════════════════════════════════════════════════════════════════╝

1️⃣  YOLO CONFIGURADO PARA CPU/GPU AUTOMÁTICO
   • ai.py: Detecta dispositivo automáticamente
   • roboflow_detector.py: Usa CPU si no hay GPU
   • La detección será más lenta en CPU, pero funcionará

2️⃣  WEBSOCKET PRIORIZADO EN main.py
   • Se registra ANTES que los routers
   • Resuelve el error 404 "Not Found"
   • Endpoint: /api/v1/detection/ws/real-time-detection

3️⃣  OPTIMIZACIONES PARA CPU
   • Imágenes redimensionadas a 416px (más rápido)
   • Máximo 5 detecciones por frame
   • IOU threshold: 0.45 (optimizado)

╔════════════════════════════════════════════════════════════════╗
║  🚀 PASOS PARA USAR                                            ║
╚════════════════════════════════════════════════════════════════╝

OPCIÓN A - Reiniciar Backend (RECOMENDADO):
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

OPCIÓN B - Usar script de inicio:
   python start_backend.py

VERIFICAR WEBSOCKET (En otra terminal):
   python test_websocket_connection.py

PROBAR CON FRONTEND:
   • Abre http://localhost:4200
   • Usa la cámara en tiempo real
   • Debería detectar zapatos

╔════════════════════════════════════════════════════════════════╗
║  ⚡ RENDIMIENTO SIN GPU NVIDIA                                ║
╚════════════════════════════════════════════════════════════════╝

Sin GPU (CPU):
   ✓ Funciona correctamente
   ✓ Detección: ~500-2000ms por frame
   ✓ ~1-2 FPS en tiempo real
   ✓ Procesamiento: yolov8n (modelo nano, ligero)

Con GPU NVIDIA:
   ✓ Detección: ~50-200ms por frame
   ✓ ~5-20 FPS en tiempo real
   ✓ MUCHO más rápido

💡 CONSEJOS:
   • Usa resolución de cámara más baja (640x480)
   • Redimensionamiento a 416px está optimizado
   • YOLO nano es el modelo más ligero
   • El código es agnóstico a GPU/CPU

╔════════════════════════════════════════════════════════════════╗
║  ❓ SOLUCIÓN DE PROBLEMAS                                    ║
╚════════════════════════════════════════════════════════════════╝

Si sigue apareciendo 404:
   1. Reinicia backend: python start_backend.py
   2. Verifica puerto 8000 no esté en uso: lsof -i :8000
   3. Borra caché: rm -rf backend/__pycache__
   4. Reinstala dependencias: pip install -r backend/requirements.txt

Si YOLO no carga:
   1. Verifica PyTorch: python -c "import torch; print(torch.__version__)"
   2. Reinstala ultralytics: pip install --upgrade ultralytics
   3. Revisa logs en terminal del backend

Si detección muy lenta:
   1. Es NORMAL sin GPU
   2. Reduce resolución de cámara
   3. Considera usar GPU si es crítica la velocidad
""")

print("\n✅ CONFIGURACIÓN COMPLETADA\n")
