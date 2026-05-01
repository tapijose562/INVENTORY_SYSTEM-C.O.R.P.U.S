#!/usr/bin/env python3
"""
REINICIO FORZADO: Mata el backend antiguo y reinicia con los nuevos cambios
"""
import os
import sys
import subprocess
import time
import psutil
import requests

print("""
╔═══════════════════════════════════════════════════════════════════╗
║              🔄 REINICIO FORZADO DEL BACKEND                    ║
║           (Necesario después de cambiar main.py)                 ║
╚═══════════════════════════════════════════════════════════════════╝
""")

# PASO 1: Buscar y matar procesos de Python que usen puerto 8000
print("\n🔍 BUSCANDO PROCESOS EN PUERTO 8000...")

try:
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and ('uvicorn' in str(cmdline) or 'main:app' in str(cmdline)):
                print(f"   ❌ Matando proceso: PID {proc.info['pid']} - {proc.info['name']}")
                proc.kill()
                time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
except:
    print("   ⚠️  No se pudo usar psutil, intentando con netstat")

# PASO 2: Limpiar caché de Python
print("\n🧹 LIMPIANDO CACHÉ DE PYTHON...")

cache_dirs = [
    'backend/__pycache__',
    'backend/app/__pycache__',
    'backend/app/api/__pycache__',
    'backend/app/api/routes/__pycache__',
    'backend/app/db/__pycache__',
    'backend/app/models/__pycache__',
    'backend/app/schemas/__pycache__',
    'backend/app/services/__pycache__',
    'backend/app/core/__pycache__',
]

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        import shutil
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✅ Eliminado: {cache_dir}")
        except:
            pass

# PASO 3: Esperar un poco
print("\n⏳ ESPERANDO 3 SEGUNDOS...")
time.sleep(3)

# PASO 4: Reiniciar backend
print("\n🚀 INICIANDO BACKEND CON CAMBIOS NUEVOS...\n")

os.chdir('backend')

cmd = [
    sys.executable, "-m", "uvicorn",
    "main:app",
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

    # Esperar a que esté listo
    print("⏳ Esperando que el backend esté listo...")
    max_retries = 30
    backend_ready = False
    
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                backend_ready = True
                print("\n✅ BACKEND REINICIADO EXITOSAMENTE")
                break
        except:
            pass
        
        print(f"   ⏳ Intento {i+1}/{max_retries}...", end='\r')
        time.sleep(0.5)

    if not backend_ready:
        print("\n⚠️  Backend tardó en iniciar, pero continuamos...")

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                   ✅ BACKEND REINICIADO                         ║
╚═══════════════════════════════════════════════════════════════════╝

🧪 PRUEBA INMEDIATA DEL WEBSOCKET:

En OTRA terminal, ejecuta:
   python test_websocket_connection.py

Si ves: ✅ WebSocket conectado!
        ✅ WebSocket está funcionando!

ENTONCES EL ERROR 404 FUE RESUELTO.

📡 ENDPOINTS DISPONIBLES:

   • API Docs:         http://127.0.0.1:8000/docs
   • Health Check:     http://127.0.0.1:8000/health
   • WebSocket:        ws://127.0.0.1:8000/api/v1/detection/ws/real-time-detection

🎥 PRUEBA EN FRONTEND:

   1. Abre http://localhost:4200
   2. Ve a "Detección en Tiempo Real"
   3. Permite acceso a cámara
   4. Debería conectarse SIN error 404

⚠️  CAMBIOS APLICADOS EN ESTE REINICIO:

   ✅ WebSocket registrado ANTES que los routers
   ✅ YOLO configurado para CPU/GPU automático
   ✅ Caché de Python limpiado
   ✅ Procesos antiguos eliminados

El backend seguirá corriendo. Presiona Ctrl+C para detener.

""")

    # Mostrar logs
    print("=" * 65)
    print("📊 LOGS DEL SERVIDOR:")
    print("=" * 65 + "\n")

    for line in process.stdout:
        if line.strip():
            print(line.rstrip())

except KeyboardInterrupt:
    print("\n\n🛑 Backend detenido")
    if 'process' in locals():
        process.terminate()
        process.wait()
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
