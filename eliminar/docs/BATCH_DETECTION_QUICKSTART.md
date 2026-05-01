# 🚀 Quick Start - Batch Detection

## ⚡ 5 Minutos para Empezar

### 1. Verificar Backend está Corriendo
```bash
cd backend
python main.py
# Output: "Application startup complete"
# Listen on: http://0.0.0.0:8000
```

### 2. Verificar Frontend está Corriendo
```bash
cd frontend
npm start
# Output: "Angular Live Development Server is listening on localhost:4200"
```

### 3. Login en http://localhost:4200/login
```
Email: admin@example.com
Password: admin123
```

### 4. Navegar a Batch Detection
Alternativa A - Directamente:
```
http://localhost:4200/batch-detection
```

Alternativa B - Desde menú (si existe):
```
Dashboard → [📸 Batch Upload] button
```

---

## 🎯 Tus Primeros Pasos

### Paso 1: Selecciona un Producto
```
Dropdown: "Selecciona un producto"
Opción: Nike Air Jordan (ID: 1) ✓ Seleccionar
```

### Paso 2: Agrega Imágenes
```
Método 1 - Click y Selecciona:
  Haz clic en la zona gris
  → File Dialog se abre
  → Selecciona 1-10 fotos JPG/PNG
  → [Abrir]

Método 2 - Drag & Drop:
  Arrastra 3 fotos sobre la zona gris
  → Las imágenes aparecen listadas
```

### Paso 3: Sube las Imágenes
```
Botón: [🚀 Subir 3 Imágenes]
↓ (carga ~2-5 segundos)
Galería se abre automáticamente
```

### Paso 4: Detecta Cada Imagen
```
En galería:
  [2/3] Imagen 2 mostrándose
  Panel derecha: [🎯 Detectar Imagen]
  → Hace clic
  → Analiza: Nike, Rojo, Size 10, $99.99, 92%
  → Resultados en panel
```

### Paso 5: Anota Selecciones
```
En canvas (imagen principal):
  Dibuja rectángulo sobre zona de interés
  → Rectángulo rojo permanente
  Panel: 📐 SELECCIÓN muestra X1, Y1, X2, Y2
  [💾 Guardar Selección] → Guardado ✅
```

### Paso 6: Termina
```
Botón: [✅ Finalizar]
→ Vuelve a dashboard limpio
```

---

## 📸 Pantalla Esperada - Galería

```
┌─────────────────────────────────────────────┐
│ 📸 Batch Image Upload & Detection           │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────┐  ┌────────────────┐  │
│  │   IMAGEN (2/3)   │  │ 🔍 DETECTAR    │  │
│  │                  │  │ Nike           │  │
│  │  [Canvas dibuja] │  │ Rojo           │  │
│  │   rectangulo]    │  │ Precio: $99.99 │  │
│  │                  │  │ 92% confianza  │  │
│  └──────────────────┘  │                │  │
│  ◀ [2/3] Siguiente▶    │ 📐 SELECCIÓN   │  │
│                        │ X1: 100, Y1:150│  │
│  [1] [2*] [3]          │ [💾 Guardar]   │  │
│                        │                │  │
│  [✅ Finalizar]        │ 📊 ESTADO      │  │
│                        │ detected ⭐    │  │
└─────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting Rápido

### Problema: "Por favor selecciona un producto"
**Solución:** Dropdown está vacío
```
1. Verifica que al menos 1 producto existe en BD
   
   Backend:
   sqlite3 backend/inventory.db
   > SELECT name FROM products LIMIT 1;
   
2. Si no hay productos:
   CREATE uno en /products
```

### Problema: Galería no carga después de upload
**Solución:** Backend error durante upload
```
1. Backend logs:
   python backend/main.py > logs.txt 2>&1
   
2. Backend health check:
   curl http://localhost:8000/docs
   → Swagger UI debe abrir
```

### Problema: Canvas no responde a dibuje
**Solución:** Canvas no tiene dimensiones
```
Recarga página: F5
Si persiste:
1. DevTools → Console
2. Escribir: document.querySelector('canvas').width
3. Debería ser > 500
```

### Problema: "N/A" en precio
**Solución:** Producto detectado no está en BD
```
Esperado: Precio solo aparece si:
- YOLO detecta marca existente
- ProductService encuentra coincidencia en BD
- Si no → N/A es OK, datos de detection siguen siendo válidos
```

### Problema: Timeout en detección (⏳ Detectando... nunca termina)
**Solución:** Backend ocupado o caído
```
1. Verifica backend sigue corriendo:
   ps aux | grep "python main.py"
   
2. Si no:
   cd backend && python main.py
   
3. Si timeout > 10s persiste:
   Revisa GPU/CUDA (si está configurado)
   python backend/test_yolo_direct.py
```

---

## ✅ Checklist de Primera Ejecución

- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 4200
- [ ] Usuario autenticado con JWT
- [ ] Al menos 1 producto existe en BD
- [ ] http://localhost:4200/batch-detection carga sin error 404
- [ ] Dropdown de productos NO está vacío
- [ ] Puedo arrastra imágenes a zona de upload
- [ ] Botón "Subir" está visible
- [ ] DevTools Console NO tiene errores (F12)

---

## 🎓 Próximos Pasos Después de Primer Test

### Si todo funciona ✅
```
1. Lee: docs/BATCH_DETECTION_INTEGRATION.md
   → Entiende la arquitectura
   
2. Ejecuta: TEST_PLAN_BATCH_DETECTION.md
   → Valida todos los casos de uso
   
3. Integra en navbar:
   → Agrega link a /batch-detection
   → Personaliza UI según tu diseño
```

### Si algo falla ❌
```
1. Verifica logs del backend:
   → tail -f backend_logs.txt
   
2. Revisa consola del navegador:
   → DevTools (F12) → Console
   
3. Busca error específico en:
   → docs/BACKEND_SETUP.md (backend issues)
   → docs/FRONTEND_SETUP.md (frontend issues)
```

---

## 📊 Estadísticas de Implementación

| Componente | Líneas | Status |
|-----------|---------|--------|
| batch-detection.component.ts | 365 | ✅ |
| batch-detection.component.html | 280 | ✅ |
| batch-detection.component.scss | 650 | ✅ |
| file-preview.pipe.ts | 12 | ✅ |
| app.routes.ts (updated) | 1 | ✅ |
| BATCH_DETECTION_INTEGRATION.md | 350+ | ✅ |
| TEST_PLAN_BATCH_DETECTION.md | 500+ | ✅ |
| **TOTAL** | **~2,200 LOC** | **✅ READY** |

---

## 🎯 Features Implementados

| Feature | Work | Status |
|---------|------|--------|
| Upload múltiples imágenes | ✅ | ✅ Completo |
| Validación máx 10 imágenes | ✅ | ✅ Completo |
| Drag & Drop | ✅ | ✅ Completo |
| Detección por imagen | ✅ | ✅ Completo |
| Galería con navegación | ✅ | ✅ Completo |
| Canvas para selecciones | ✅ | ✅ Completo |
| Marcar principal | ✅ | ✅ Completo |
| Eliminar imagen | ✅ | ✅ Completo |
| Responsivo (mobile) | ✅ | ✅ Completo |
| Error handling | ✅ | ✅ Completo |

---

## 🔗 Links Útiles

| Link | Propósito |
|------|-----------|
| http://localhost:4200/batch-detection | Batch Detection UI |
| http://localhost:4200/detection | Single Detection (original) |
| http://localhost:8000/docs | API Swagger |
| http://localhost:8000/api/v1/product-images | API endpoint |
| docs/BATCH_DETECTION_INTEGRATION.md | Documentación técnica |
| docs/TEST_PLAN_BATCH_DETECTION.md | Suite de pruebas |

---

## 💡 Tips & Tricks

### Tip 1: Usar Teclado
```
Tab → Navega entre botones
Enter → Presiona botón enfocado
Escape → Cancela operación (si aplica)
```

### Tip 2: Optimizar Upload
```
✅ Imagenes recomendadas:
   - Formato: JPEG (mejor compresión)
   - Tamaño: 500x500 a 1920x1440px
   - File size: 100KB-2MB por imagen
   
❌ Evitar:
   - PNG de 10MB (muy pesado)
   - Imágenes borrosas (no detecta bien)
   - Archivos en formato raro (.bmp, .tiff)
```

### Tip 3: Debug en DevTools
```javascript
// En console (F12):
// Ver estado del componente:
ng.probe(document.querySelector('app-batch-detection'))
  .componentInstance

// Ver últimos resulados:
this.currentDetection

// Ver todas las imágenes:
this.images
```

### Tip 4: Seguridad del Local Storage
```javascript
// El componente NO guarda en localStorage
// Todo es ephemeral hasta hacer clic "Guardar"
// → Refrescar página limpia estado
```

---

## 📞 Support

Para casos no cubiertos:

1. **Errores de Backend:**
   - Revisar `backend/main.py` stderr
   - Ejecutar `backend/diagnose_system.py`
   - Verificar BD: `sqlite3 backend/inventory.db ".schema"`

2. **Errores de Frontend:**
   - DevTools Console (F12)
   - Network tab para ver requests/responses
   - Check CORS headers

3. **Problemas de IA/Detección:**
   - Ejecutar: `backend/test_yolo_direct.py`
   - Ejecutar: `backend/test_ocr_isolated.py`
   - Revisar: `docs/ML_PIPELINE.md`

---

**¡Listo para comenzar! 🚀**

Ejecuta `npm start` + `python main.py` + navega a `/batch-detection`

¿Preguntas? Revisa `docs/` o abre un issue.
