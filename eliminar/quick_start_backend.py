#!/usr/bin/env python3
"""
🚀 QUICK START: Inicia el backend con diagnóstico automático
"""

import subprocess
import time
import sys
import os
import requests
import json

print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    🚀 INVENTORY CORPUS v2 - QUICK START          ║
║                   Sistema de Detección SIN GPU NVIDIA             ║
╚═══════════════════════════════════════════════════════════════════╝
""")

# 1. Verificar Python y dependencias
print("\n📋 VERIFICANDO REQUISITOS...")

try:
    import torch
    device_type = "🟢 GPU NVIDIA" if torch.cuda.is_available() else "🔵 CPU"
    print(f"   ✅ PyTorch {torch.__version__} ({device_type})")
except:
    print("   ❌ PyTorch no encontrado - ejecuta: pip install torch ultralytics")
    sys.exit(1)

try:
    import fastapi
    print(f"   ✅ FastAPI")
except:
    print("   ❌ FastAPI no encontrado - ejecuta: pip install fastapi uvicorn")
    sys.exit(1)

# 2. Iniciar backend
print("\n🚀 INICIANDO BACKEND...")
print("   (Presiona Ctrl+C para detener)\n")

# Determinar el comando según el SO
if sys.platform.startswith("win"):
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]
else:
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]

try:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    # Esperar a que el servidor esté listo
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("\n" + "="*65)
                print("✅ BACKEND INICIADO EXITOSAMENTE")
                print("="*65)
                break
        except:
            print(f"   ⏳ Esperando backend... ({i+1}/{max_retries})", end='\r')
            time.sleep(0.5)
    else:
        print("\n❌ Backend tardó mucho en iniciar")
        sys.exit(1)

    # 3. Verificar endpoints principales
    print("\n📡 VERIFICANDO ENDPOINTS:\n")

    endpoints = [
        ("Health Check", "http://127.0.0.1:8000/health"),
        ("Swagger UI", "http://127.0.0.1:8000/docs"),
        ("ReDoc", "http://127.0.0.1:8000/redoc"),
    ]

    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=2)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {name}: {url}")
        except:
            print(f"   ❌ {name}: No disponible")

    # 4. Información importante
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     ℹ️  INFORMACIÓN IMPORTANTE                   ║
╚═══════════════════════════════════════════════════════════════════╝

🌐 URLs DE ACCESO:

   • Frontend:        http://localhost:4200
   • API Swagger:     http://127.0.0.1:8000/docs
   • API ReDoc:       http://127.0.0.1:8000/redoc
   • WebSocket:       ws://127.0.0.1:8000/api/v1/detection/ws/real-time-detection

🎥 PRUEBA DE CÁMARA EN TIEMPO REAL:

   1. Abre http://localhost:4200 en tu navegador
   2. Ve a la sección de "Detección en Tiempo Real"
   3. Permite acceso a la cámara
   4. Apunta a zapatos y debería detectarlos

⚡ RENDIMIENTO ESPERADO:

   Sin GPU NVIDIA (CPU):     1-2 FPS (normal, funciona correctamente)
   Con GPU NVIDIA:           5-20 FPS (mucho más rápido)

🔧 CONFIGURACIÓN ACTUAL:

   Dispositivo: {device_type}
   Modelo YOLO: yolov8n (nano, muy ligero)
   Optimizaciones: CPU habilitadas
   Puerto API: 8000
   CORS: http://localhost:4200

📝 CAMBIOS REALIZADOS PARA FUNCIONAR SIN GPU:

   ✅ YOLO configurado para detectar GPU/CPU automáticamente
   ✅ WebSocket priorizado en main.py
   ✅ Optimizaciones para CPU incluidas
   ✅ Imágenes redimensionadas a 416px
   ✅ Máximo 5 detecciones por frame

🐛 SOLUCIÓN DE PROBLEMAS:

   Si ves error 404 en WebSocket:
   → Reinicia el backend (Ctrl+C y vuelve a ejecutar este script)
   → Limpia caché: del backend/__pycache__

   Si YOLO no carga:
   → Verifica: pip show ultralytics
   → Reinstala: pip install --upgrade ultralytics

   Si muy lento (normal sin GPU):
   → Reduce resolución de cámara
   → Es normal 1-2 FPS en CPU

╔═══════════════════════════════════════════════════════════════════╗
║                  ✅ LISTO PARA USAR                              ║
╚═══════════════════════════════════════════════════════════════════╝

Abre otra terminal y ejecuta:
   • Frontend:  cd frontend && ng serve
   • Tests:     python test_websocket_connection.py

El backend seguirá corriendo en esta terminal.
Presiona Ctrl+C para detener.

""")

    # Mostrar logs del servidor
    print("\n📊 LOGS DEL SERVIDOR:\n")
    print("-" * 65)
    
    for line in process.stdout:
        print(line.rstrip())

except KeyboardInterrupt:
    print("\n\n🛑 Backend detenido por el usuario")
    process.terminate()
    process.wait()
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
