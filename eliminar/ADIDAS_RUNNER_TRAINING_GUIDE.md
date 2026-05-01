# 🚀 Guía Completa: Registro y Entrenamiento del Adidas Runner

## 🎯 Objetivo
Registrar el Adidas Runner (azul marino y blanco) en el sistema y entrenar el modelo YOLO para que lo reconozca automáticamente en tiempo real a través de la cámara.

---

## 📋 Tabla de Contenidos
1. [Preparar Imágenes](#-paso-1-preparar-imágenes)
2. [Registrar Producto](#-paso-2-registrar-producto)
3. [Subir Imágenes](#-paso-3-subir-imágenes)
4. [Entrenar YOLO](#-paso-4-entrenar-yolo)
5. [Probar en Tiempo Real](#-paso-5-probar-en-tiempo-real)

---

## 📁 Paso 1: Preparar Imágenes

### Ubicación de Images
```
📂 assets/images/adidas_runner/
```

### Instrucciones:
1. **Copia las 6 imágenes del Adidas Runner** que se proporcionaron
2. **Renombralas así:**
   ```
   adidas_runner_001.png
   adidas_runner_002.png
   adidas_runner_003.png
   adidas_runner_004.png
   adidas_runner_005.png
   adidas_runner_006.png
   ```

3. **Coloca adicionales si es posible:**
   - Mínimo recomendado: **20-30 imágenes**
   - Desde diferentes ángulos:
     * Vista frontal (desde arriba)
     * Vista lateral izquierda (45°)
     * Vista lateral derecha (45°)
     * Vista posterior
     * Diferentes alturas
   - Bajo diferentes iluminaciones:
     * Luz natural
     * Luz artificial
     * Diferentes intensidades

### ✅ Status:
- [x] Carpeta creada: `assets/images/adidas_runner/`
- [ ] Imágenes copiadas (0 encontradas actualmente)
- [ ] Mínimo 20-30 imágenes disponibles

---

## ✍️ Paso 2: Registrar Producto

### Datos del Producto:
```json
{
  "name": "Adidas Runner",
  "brand": "Adidas",
  "colors": "Navy Blue / White",
  "color_primary": "Navy Blue",
  "color_secondary": "White",
  "size": "42",
  "stock": 10,
  "price": 12599,
  "description": "Adidas Running Shoe - Navy Blue with White Accents",
  "color_rgb": {
    "r": 0,
    "g": 51,
    "b": 102
  }
}
```

### Opción A: Vía Frontend (Recomendado)
1. Abre: **http://localhost:4200**
2. Ve a: **📦 Products > Create New Product**
3. Ingresa los datos exactamente como se muestran arriba
4. Click: **"Create Product"**
5. **Copia el ID del producto** que aparecerá en la respuesta

### Opción B: Vía Terminal
```bash
# Ejecutar este comando en PowerShell:
$product = @{
    name = "Adidas Runner"
    brand = "Adidas"
    colors = "Navy Blue / White"
    color_primary = "Navy Blue"
    color_secondary = "White"
    size = "42"
    stock = 10
    price = 12599
    description = "Adidas Running Shoe"
    color_rgb = @{r = 0; g = 51; b = 102}
    yolo_confidence = 0.85
    detection_metadata = @{shoe_type = "running"}
}

$json = $product | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/products" `
  -Method POST `
  -Body $json `
  -ContentType "application/json"
```

### ✅ Status:
- [ ] Backend corriendo en: http://localhost:8000
- [ ] Producto registrado exitosamente
- [ ] ID del producto: `_______________`

---

## 🖼️ Paso 3: Subir Imágenes

### Opción A: Vía Frontend (Recomendado)
1. Ve a: **http://localhost:4200**
2. Navega a: **📦 Products**
3. Busca: **"Adidas Runner"**
4. Click en el producto
5. Busca la sección: **"📷 Upload Images"**
6. **Arrastra las imágenes** (o selecciona una carpeta)
7. El sistema:
   - ✅ Validará cada imagen
   - ✅ Las guardará en el servidor
   - ✅ Actua lizará la lista del producto

### Opción B: Vía Terminal (cURL)
```bash
# Para cada imagen:
curl -X POST http://localhost:8000/api/v1/product-images \
  -H "Content-Type: multipart/form-data" \
  -F "product_id={PRODUCT_ID}" \
  -F "file=@assets/images/adidas_runner/adidas_runner_001.jpg"
```

### ✅ Status:
- [ ] Al menos 5 imágenes subidas
- [ ] Mínimo 20-30 imágenes subidas (ideal)
- [ ] Todas las imágenes validadas

---

## 🤖 Paso 4: Entrenar YOLO

### Timeline de Entrenamiento:
- ⏱️ **Con GPU (NVIDIA CUDA):** 5-10 minutos
- ⏱️ **Sin GPU:** 15-30 minutos
- ⏱️ **CPU lento:** 1-2 horas

### Vía Frontend (Recomendado):
1. Ve a: **http://localhost:4200**
2. Navega a: **🎓 Training**
3. Click en: **"Train New Model"**
4. El sistema:
   - ✅ Detectará automáticamente las imágenes del Adidas Runner
   - ✅ Creará el dataset de entrenamiento
   - ✅ Entrenará durante 20 épocas
   - ✅ Guardará el modelo actualizado

### Monitorea en tiempo real:
```
Epoch 1/20 ▮▮░░░░░░░░ 5%
Loss: 0.89
Precision: 0.82
Recall: 0.78
mAP50: 0.80
ETA: 8m 45s
```

### Resultados Esperados:
| Métrica | Objetivo | Rango |
|---------|----------|-------|
| **Precision** | > 0.90 | 0.85-0.95 |
| **Recall** | > 0.85 | 0.80-0.92 |
| **mAP50** | > 0.85 | 0.80-0.95 |
| **Status** | GREEN | ✅ Exitoso |

### ✅ Status:
- [ ] Entrenamiento iniciado
- [ ] Monitoreo en tiempo real visible
- [ ] Entrenamiento completado exitosamente
- [ ] Status: GREEN (Modelo listo)

---

## ⚡ Paso 5: Probar en Tiempo Real

### Iniciar Detección en Tiempo Real:
1. Ve a: **http://localhost:4200**
2. Navega a: **🔍 Detection**
3. Busca: **"⚡ Real-Time Detection Mode (Beta)"**
4. Click: **"Start Real-Time Detection"**
5. **Permitir acceso a cámara** (cuando lo pida el navegador)

### Presenta el Adidas Runner:
📹 **Posiciones recomendadas:**
```
1. Frontal (vista superior) → 45°
2. Lateral izquierda → 90°
3. Lateral derecha → 90°
4. Trasera → frontal
5. Diferentes ángulos dinámicamente
```

### El sistema debe mostrar:
```
┌─────────────────────────────────┐
│ 🔍 Real-Time Detection Results  │
├─────────────────────────────────┤
│ ✅ Brand: "Adidas"              │
│ ✅ Colors: "Navy Blue / White"  │
│ ✅ Size: "42"                   │
│ ✅ Confidence: 0.92 (92%)       │
│ ✅ Price: "$125.99"             │
│ ✅ FPS: 24                      │
│ ⏱️  Detection Time: 45ms        │
└─────────────────────────────────┘
```

### Dashboard en Tiempo Real:
```
📊 DETECTION HISTORY
─────────────────────
1. [00:01] Adidas Runner detected ✅
2. [00:03] Adidas Runner detected ✅
3. [00:05] Adidas Runner detected ✅
4. [00:07] No object detected
5. [00:09] Adidas Runner detected ✅

📈 ACCURACY: 80% (4/5 frames)
⚡ AVG FPS: 24 fps
⏱️  AVG TIME: 45ms/frame
```

### Guardar Resultados:
- ✅ Cada detección se registra automáticamente
- ✅ Los datos se almacenan para futuras mejoras
- ✅ El modelo se optimiza con los datos

### ✅ Status:
- [ ] Cámara accesible y funcionando
- [ ] Detección en tiempo real iniciada
- [ ] Adidas Runner reconocido >0.85 precisión
- [ ] Métricas mostradas en pantalla
- [ ] Todas las detecciones guardadas

---

## 🔄 Paso 6: Mejora Iterativa (Opcional)

### Ciclo de Mejora Continua:
```
1️⃣ Recopilar más imágenes
        ↓
2️⃣ Subir nuevas imágenes
        ↓
3️⃣ Re-entrenar modelo
        ↓
4️⃣ Probar en tiempo real
        ↓
5️⃣ Validar mejoras
        ↓
    (Volver al paso 1 si es necesario)
```

### Cómo mejorar la precisión:
1. **Más datos:**
   - Recopila 100+ imágenes
   - Cubre más ángulos y condiciones
   - Diferentes fondos y iluminaciones

2. **Aumentación de datos:**
   - Rotaciones
   - Escalas
   - Recortes aleatorios

3. **Re-entrenar:**
   - Usa epochs adicionales (30-50 total)
   - Ajusta el learning rate

4. **Validar:**
   - Prueba en diferentes entornos
   - Diferentes luz
   - Diferentes distancias

---

## 📋 Checklist Completo

```
☐ 1. Imágenes copiadas a assets/images/adidas_runner/
☐ 2. Carpeta preparada y confirmada
☐ 3. Producto "Adidas Runner" registrado
☐ 4. ID del producto documentado: _______________
☐ 5. Mínimo 20-30 imágenes subidas
☐ 6. Todas las imágenes validadas
☐ 7. Modelo YOLO entrenado exitosamente
☐ 8. Status del modelo: GREEN
☐ 9. Cámara funcionando en tiempo real
☐ 10. Adidas Runner detectado con >0.85 precisión
☐ 11. Todas las métricas mostrando correctamente
☐ 12. Detecciones guardadas en la BD
```

---

## 🆘 Solución de Problemas

### Problema: Backend no responde
```
❌ Error: Connection refused (localhost:8000)
✅ Solución: Asegúrate que el backend está corriendo:
   cd backend
   python main.py
```

### Problema: Imágenes no se suben
```
❌ Error: 400 Bad Request
✅ Solución:
   • Verifica que las imágenes son .jpg o .png
   • Tamaño mínimo: 100x100px
   • Tamaño máximo: 50MB por imagen
   • Formato correcto: JPEG/PNG validado
```

### Problema: Entrenamiento lento
```
❌ Error: Taking too long...
✅ Solución:
   • Usar GPU: instala CUDA + cuDNN
   • Reducir imágenes a 640x640
   • Disminuir batch size a 8
   • Usar modelo más pequeño: yolov8s.pt
```

### Problema: Detección imprecisa
```
❌ Error: Low confidence (<0.7)
✅ Solución:
   • Recolecta más imágenes (100+)
   • Varía más los ángulos y fondos
   • Re-entrena con más épocas (30-50)
   • Asegúrate de iluminación consistente
```

### Problema: Cámara no funciona
```
❌ Error: Camera access denied
✅ Solución:
   • Otorga permisos de cámara al navegador
   • Recarga la página (F5)
   • Intenta en navegador diferente
   • Reinicia el navegador
```

---

## 📞 Comandos Útiles

### Verificar backend:
```bash
# En PowerShell
curl http://localhost:8000/docs
```

### Ver logs del backend:
```bash
# En la terminal del backend
# Los logs aparecen automáticamente
```

### Listar imágenes subidas:
```bash
# En PowerShell
Get-ChildItem assets/images/adidas_runner/ | Format-Table Name
```

### Limpiar imágenes antigas:
```bash
# En PowerShell (CUIDADO: Irreversible)
Remove-Item assets/images/adidas_runner/* -Exclude "adidas_runner_*.jpg"
```

---

## 🎓 Recursos Adicionales

- **YOLO Documentation:** https://docs.ultralytics.com/
- **Object Detection:** https://en.wikipedia.org/wiki/Object_detection
- **Computer Vision:** https://opencv.org/
- **Deep Learning:** https://pytorch.org/

---

## 🏆 Resultado Final

Cuando completes todos los pasos, el sistema:

```
✅ Registrará el Adidas Runner en la base de datos
✅ Almacenará 20-30+ imágenes de entrenamiento
✅ Entrenará un modelo YOLO específico para Adidas
✅ Detectará automáticamente el zapato en tiempo real
✅ Mostrará: Marca, Colores, Talla, Precio y Confianza
✅ Guardará un historial de todas las detecciones
✅ Mejorará continuamente con cada uso
```

**¡Cuando presentes el Adidas Runner a la cámara, 
el sistema lo reconocerá automáticamente! 🎯**

---

**Status:** ✅ Guía Completa Lista
**Versión:** 1.0
**Última actualización:** Abril 11, 2026
