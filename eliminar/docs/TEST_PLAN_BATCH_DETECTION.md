# Test Plan - Batch Image Detection

## 🧪 Pruebas Funcionales Completas

### Prerequisitos
- ✅ Backend corriendo en localhost:8000
- ✅ Frontend corriendo en localhost:4200
- ✅ Usuario autenticado (JWT token)
- ✅ Al menos 1 producto creado en BD

---

## 📋 Suite de Pruebas Funcionales

### Test Suite 1: Carga de Imágenes

#### TC-1.1: Seleccionar Imágenes por Diálogo
**Pasos:**
1. Navegar a `/batch-detection`
2. Hacer clic en "Arrastra imágenes aquí"
3. En diálogo, seleccionar 3 imágenes JPG/PNG

**Resultado Esperado:**
- ✅ Las 3 imágenes aparecen listadas
- ✅ Muestra "3 / 10 imágenes seleccionadas"
- ✅ Previsualizaciones visible en cada thumbnail
- ✅ Botón "Subir" ahora está habilitado

---

#### TC-1.2: Drag & Drop de Imágenes
**Pasos:**
1. Navegar a `/batch-detection`
2. Arrastrar 5 imágenes sobre la zona de drop
3. Soltar las imágenes

**Resultado Esperado:**
- ✅ Zona de drop cambia color (activa)
- ✅ Las 5 imágenes aparecen en lista
- ✅ Contador muestra "5 / 10"
- ✅ No hay duplicados

---

#### TC-1.3: Validación de Máximo 10 Imágenes
**Pasos:**
1. Seleccionar 10 imágenes
2. Intentar arrastrar una imagen más

**Resultado Esperado:**
- ✅ Muestra error: "Ya has seleccionado el máximo de 10 imágenes"
- ✅ La imagen adicional NO se agrega
- ✅ Contador sigue siendo "10 / 10"

---

#### TC-1.4: Remover Imagen de Lista
**Pasos:**
1. Seleccionar 5 imágenes
2. Hacer clic en 🗑️ de la 3ª imagen

**Resultado Esperado:**
- ✅ La imagen se elimina de la lista
- ✅ Contador ahora muestra "4 / 10"
- ✅ Las otras imágenes se reorganizan

---

#### TC-1.5: Validación - Producto Requerido
**Pasos:**
1. Seleccionar 3 imágenes
2. Dejar dropdown de producto vacío
3. Hacer clic en "Subir 3 Imágenes"

**Resultado Esperado:**
- ✅ Muestra error: "Por favor selecciona un producto"
- ✅ No se hace POST a /upload-batch
- ✅ Las imágenes siguen en la lista

---

### Test Suite 2: Upload a Servidor

#### TC-2.1: Upload Exitoso
**Pasos:**
1. Seleccionar producto "Nike Air Jordan"
2. Seleccionar 3 imágenes
3. Hacer clic "Subir 3 Imágenes"

**Resultado Esperado:**
- ✅ Muestra overlay "⏳ Subiendo imágenes..."
- ✅ POST a `/api/v1/product-images/upload-batch` se completa
- ✅ Transición automática a modo "gallery"
- ✅ Se muestran todas las 3 imágenes

**Backend Validation:**
```bash
# Verificar tabla product_images
SELECT * FROM product_images WHERE product_id = 1;
# Debe haber 3 registros con status="pending"
```

---

#### TC-2.2: Upload con Error de Red
**Pasos:**
1. Desconectar internet
2. Seleccionar 2 imágenes y producto
3. Hacer clic "Subir 2 Imágenes"
4. Esperar timeout (5 segundos)

**Resultado Esperado:**
- ✅ Toast rojo: "❌ [Error de red]"
- ✅ Permanece en modo "upload"
- ✅ Las imágenes siguen seleccionadas

---

#### TC-2.3: Upload con Error Backend (max 10)
**Pasos:**
1. Producto ya tiene 8 imágenes (setup previo)
2. Intentar subir 5 imágenes más

**Resultado Esperado:**
- ✅ Backend retorna 400 Bad Request
- ✅ Toast muestra: "❌ Límite de 10 imágenes excedido"
- ✅ Permanece en upload, no hace transición

---

### Test Suite 3: Galería de Imágenes

#### TC-3.1: Navegación Básica
**Pasos:**
1. Upload 3 imágenes exitoso
2. Verificar contador "1 / 3"
3. Hacer clic "Siguiente ▶"
4. Verificar "2 / 3"
5. Hacer clic "Siguiente ▶"
6. Verificar "3 / 3"
7. Hacer clic "Siguiente" (deshabilitado)
8. Hacer clic "◀ Anterior"
9. Verificar "2 / 3"

**Resultado Esperado:**
- ✅ Navegación correcta entre imágenes
- ✅ Botones deshabilitados en extremos
- ✅ Canvas se limpia cuando cambias imagen
- ✅ Selección anterior NO persiste

---

#### TC-3.2: Click en Miniatura
**Pasos:**
1. Upload 4 imágenes
2. Hacer clic en miniatura [3]

**Resultado Esperado:**
- ✅ Miniatura [3] se resalta (borde azul)
- ✅ Contador cambia a "3 / 4"
- ✅ Imagen principal muestra imagen 3
- ✅ Canvas se limpia

---

#### TC-3.3: Mostrar Miniaturas Solo Primeras 5
**Pasos:**
1. Upload 10 imágenes
2. Verificar galería de miniaturas

**Resultado Esperado:**
- ✅ Se muestran todas las 10 miniaturas
- ✅ Scroll horizontal si es necesario (responsive)
- ✅ Todas las miniaturas son clickeables

---

### Test Suite 4: Detección Individual

#### TC-4.1: Ejecutar Detección Exitosa
**Pasos:**
1. En galería, imagen actual = 1
2. Hacer clic "🎯 Detectar Imagen"
3. Esperar procesamiento (~3 segundos)

**Resultado Esperado:**
- ✅ Botón muestra "⏳ Detectando..."
- ✅ Panel se llena con datos:
  - Marca: [e.g., "Nike"]
  - Color: [e.g., "Rojo"] (color box visible)
  - Tamaño: [e.g., "42"]
  - Precio: [e.g., "$89.99"]
  - Confianza: [e.g., "92%"]
- ✅ `images[0].status` se actualiza a "detected"

**Backend Validation:**
```bash
# Verificar UPDATE en product_images
SELECT * FROM product_images WHERE id = [image_id];
# Debe tener detected_brand, detected_color, detected_size, price > NULL
```

---

#### TC-4.2: Detección en Imagen 2
**Pasos:**
1. Navegador a imagen 2
2. Hacer clic "🎯 Detectar Imagen"
3. Esperar resultado

**Resultado Esperado:**
- ✅ Detección de imagen 2 completa
- ✅ Datos de imagen 1 se mantienen en BD
- ✅ Cada imagen tiene sus propios resultados

---

#### TC-4.3: Detección Fallida (sin YOLO)
**Pasos:**
1. Imagen completamente negra (setup)
2. Hacer clic "🎯 Detectar Imagen"

**Resultado Esperado:**
- ✅ Toast: "❌ Detección no pudo procesar"
- ✅ Panel muestra error en lugar de resultados
- ✅ Status permanece "pending"
- ✅ No se congela interfaz

---

### Test Suite 5: Selección en Canvas

#### TC-5.1: Dibujar Selección
**Pasos:**
1. Tener detección exitosa en imagen 1
2. En canvas, hacer click izq. en (100,100)
3. Arrastrar a (200,200)
4. Soltar

**Resultado Esperado:**
- ✅ Se dibuja rectángulo verde mientras arrastras
- ✅ Después de soltar, se dibuja rectángulo rojo permanente
- ✅ Panel "SELECCIÓN" muestra:
  - X1: 100, Y1: 100
  - X2: 200, Y2: 200
  - W: 100, H: 100
- ✅ Botón "💾 Guardar Selección" se habilita

---

#### TC-5.2: Dibujar Selección Inválida (muy pequeña)
**Pasos:**
1. En canvas, dibujar línea de 5 píxeles

**Resultado Esperado:**
- ✅ Canvas NO muestra selección
- ✅ `currentSelection` = null
- ✅ Botón "Guardar Selección" permanece deshabilitado

---

#### TC-5.3: Redibujar Selección
**Pasos:**
1. Hacer selección 1: (100,100) → (200,200)
2. Hacer selección 2: (300,300) → (400,400)

**Resultado Esperado:**
- ✅ La selección 1 desaparece
- ✅ Solo se dibuja selección 2
- ✅ Panel actualiza con coords de selección 2

---

#### TC-5.4: Guardar Selección
**Pasos:**
1. Hacer selección válida
2. Hacer clic "💾 Guardar Selección"

**Resultado Esperado:**
- ✅ PATCH a `/api/v1/product-images/{image_id}`
- ✅ Alert: "✅ Selección guardada"
- ✅ `images[currentIndex].status` = "annotated"
- ✅ Miniatura muestra ícono de "annotated"

**Backend Validation:**
```bash
SELECT * FROM product_images WHERE id = [image_id];
# selection_data debe contener JSON: {"x1": 100, "y1": 100, ...}
```

---

### Test Suite 6: Gestión de Imágenes Primarias

#### TC-6.1: Marcar Como Principal
**Pasos:**
1. Upload 3 imágenes
2. Imagen 1 seleccionada (por defecto)
3. Navega a imagen 2
4. Hacer clic "⭐ Hacer Principal"

**Resultado Esperado:**
- ✅ POST a `/api/v1/product-images/{image_2_id}/set-primary`
- ✅ Miniatura 2 muestra ⭐
- ✅ Miniatura 1 ya no muestra ⭐
- ✅ Imagen 2 cambia a `is_primary = 1`

**Backend Validation:**
```bash
SELECT is_primary FROM product_images WHERE product_id = [id];
# Solo una debe tener is_primary = 1
```

---

#### TC-6.2: Solo Una Principal Permitida
**Pasos:**
1. Imagen 2 es principal (⭐)
2. Navega a imagen 3
3. Hacer clic "⭐ Hacer Principal"
4. Vuelve a imagen 1 y 2

**Resultado Esperado:**
- ✅ Imagen 2: is_primary = 0 (⭐ desaparece)
- ✅ Imagen 3: is_primary = 1 (⭐ aparece)
- ✅ Botón en imagen 3: deshabilitado

---

### Test Suite 7: Eliminación de Imágenes

#### TC-7.1: Eliminar Imagen
**Pasos:**
1. Upload 3 imágenes
2. Imagen 1 activa
3. Hacer clic "🗑️ Eliminar" en panel

**Resultado Esperado:**
- ✅ Confirm dialog: "¿Estás seguro...?"
- ✅ Hacer clic "Aceptar"
- ✅ DELETE a `/api/v1/product-images/{image_1_id}`
- ✅ Imagen 1 desaparece
- ✅ `images[].length` = 2
- ✅ Vista cambia a imagen 2 automáticamente

**Backend Validation:**
```bash
SELECT COUNT(*) FROM product_images WHERE product_id = [id];
# Debe devolver 2 (era 3)
# Archivo físico en /uploads/ debe estar eliminado
```

---

#### TC-7.2: Cancelar Eliminación
**Pasos:**
1. Upload 3 imágenes
2. Hacer clic "🗑️ Eliminar"
3. Confirm dialog → "Cancelar"

**Resultado Esperado:**
- ✅ No se ejecuta DELETE
- ✅ Imagen permanece en galería
- ✅ Contador sigue "3 / 3"

---

#### TC-7.3: Eliminar Imagen Principal
**Pasos:**
1. Upload 3 imágenes
2. Imagen 1 es principal (is_primary=1)
3. Hacer clic "🗑️ Eliminar" en imagen 1
4. Confirmar

**Resultado Esperado:**
- ✅ Imagen 1 se elimina
- ✅ Sistema automáticamente asigna is_primary a imagen 2
- ✅ Miniatura 2 ahora muestra ⭐

---

### Test Suite 8: Error Handling & Edge Cases

#### TC-8.1: Desconexión Durante Upload
**Pasos:**
1. Iniciar upload de 5 imágenes
2. Luego de 2 segundos, desactivar WiFi/ethernet
3. Esperar timeout

**Resultado Esperado:**
- ✅ Error toast visible
- ✅ Permanece en "upload" mode
- ✅ Imágenes siguen seleccionadas
- ✅ Usuario puede reintentar

---

#### TC-8.2: Token Expirado Durante Galería
**Pasos:**
1. Upload exitoso, en galería
2. Token expira (esperar o editar manualmente en DevTools)
3. Hacer clic "🎯 Detectar Imagen"

**Resultado Esperado:**
- ✅ 401 Unauthorized
- ✅ Redirige a `/login`
- ✅ Toast: "Sesión expirada, por favor inicia sesión"

---

#### TC-8.3: Producto Eliminado Después de Upload
**Pasos:**
1. Upload 3 imágenes al producto "Nike"
2. En otra pestaña, eliminar producto "Nike"
3. En galería, hacer clic "Guardar Selección"

**Resultado Esperado:**
- ✅ 404 Not Found (producto no existe)
- ✅ Error toast: "Producto no encontrado"
- ✅ Opción para volver a dashboard

---

#### TC-8.4: Imagen No Encuentra Precio
**Pasos:**
1. Upload imagen de producto desconocido
2. Ejecutar detección

**Resultado Esperado:**
- ✅ Detección completa sin error
- ✅ Precio = "N/A" (no se encuentra)
- ✅ Otros campos (marca, color, etc.) completos
- ✅ No bloquea UI

---

### Test Suite 9: UI/UX Responsividad

#### TC-9.1: Desktop (1400px)
**Pasos:**
1. Abrir en desktop 1920x1200
2. Upload 3 imágenes
3. En galería

**Resultado Esperado:**
- ✅ Imagen a la izquierda (70%)
- ✅ Panel derecha (30%)
- ✅ Miniaturas abajo completo ancho
- ✅ Todo visible sin scroll horizontal

---

#### TC-9.2: Tablet (800px)
**Pasos:**
1. Redimensionar a 800x600 (DevTools)
2. Upload y galería

**Resultado Esperado:**
- ✅ Imagen y panel apilan verticalmente
- ✅ Panel toma 100% ancho
- ✅ Miniaturas grilladas responsivas
- ✅ Scroll vertical funcional

---

#### TC-9.3: Mobile (375px)
**Pasos:**
1. Redimensionar a 375x667 (iPhone SE)
2. Upload y galería

**Resultado Esperado:**
- ✅ Imagen 100% ancho
- ✅ Panel 100% ancho abajo
- ✅ Botones full-width legibles
- ✅ Canvas toca a vista en toques

---

#### TC-9.4: Validación de Teclado
**Pasos:**
1. En galería
2. Presionar Tab reiteradamente

**Resultado Esperado:**
- ✅ Orden lógico de tabulación
- ✅ Botones reciben `:focus` visible
- ✅ Inputs tabulables correctamente

---

### Test Suite 10: Performance & Load

#### TC-10.1: Upload 10 Imágenes Grandes (5MB cada una)
**Pasos:**
1. Generar 10 imágenes de 5MB cada una
2. Upload todas

**Resultado Esperado:**
- ✅ Upload completa en <30 segundos
- ✅ No congelamiento de UI
- ✅ Progress visible (overlay)
- ✅ Todas las 10 se cargan en galería

---

#### TC-10.2: Detección Secuencial en 10 Imágenes
**Pasos:**
1. Upload 10 imágenes
2. Ejecutar detección en cada una (secuencial)

**Resultado Esperado:**
- ✅ Cada detección toma ~2-3 segundos
- ✅ Una detección anterior no interfiere con siguiente
- ✅ Canvas se limpia correctamente
- ✅ Memory leaks: NO (checker en DevTools)

---

#### TC-10.3: Las 10 Imágenes + Miniaturas Rendering
**Pasos:**
1. Upload 10 imágenes
2. Navega rápidamente entre imágenes

**Resultado Esperado:**
- ✅ Rendering fluido (>30 FPS)
- ✅ Canvas redraw sin lag
- ✅ Miniaturas cargan smooth

---

### Test Suite 11: Integración con Sistema Existente

#### TC-11.1: Producto Creado en Batch Aparece en /products
**Pasos:**
1. Crear producto "Test Shoe" en batch-detection
2. Upload 1 imagen primaria, salvar
3. Ir a `/products`

**Resultado Esperado:**
- ✅ "Test Shoe" aparece en lista
- ✅ Imagen primaria es el thumbnail
- ✅ Datos de detección visibles

---

#### TC-11.2: Cambiar a /detection Desde Batch
**Pasos:**
1. En batch-detection, hacer clic "← Back to Detection"

**Resultado Esperado:**
- ✅ Navega a `/detection`
- ✅ Layout "single detection" visible
- ✅ Batch data NO persiste (clean state)

---

#### TC-11.3: Logout y Relogin
**Pasos:**
1. En batch-detection
2. Hacer logout
3. Relogin
4. Ir a `/batch-detection`

**Resultado Esperado:**
- ✅ AuthGuard redirige a `/login` (sin token)
- ✅ Después de relogin, `/batch-detection` accesible
- ✅ Estado anterior se perdió (limpio)

---

## 🧪 Suite de Pruebas Técnicas (Develarers)

### Test T-1: Validación de Tipos TypeScript
```bash
# En terminal frontend
ng build --strict

# Esperado: ✅ 0 errores de tipo
```

### Test T-2: Lint ESLint
```bash
# En terminal frontend
npm run lint

# Esperado: ✅ 0 errores, 0 warnings
```

### Test T-3: Memory Leaks (Canvas)
**pasos:**
1. Abrir DevTools → Memory
2. Tomar snapshot 1
3. Upload 10 imágenes
4. Detectar cada una
5. Borrar todas
6. Garbage collect
7. Tomar snapshot 2

**Resultado Esperado:**
- ✅ Snapshot 2 similar o menor que Snapshot 1
- ✅ No hay referencias a elementos eliminados

---

### Test T-4: Red Team - XSS

#### Test T-4.1: Nombre de Producto Malicioso
```
Producto name: "<script>alert('XSS')</script>"
```

**Resultado Esperado:**
- ✅ Script NO se ejecuta
- ✅ Se muestra como texto literal
- ✅ Backend sanitiza/escapa

---

#### Test T-4.2: Filename Traversal
```
Intento acceder: /file/../../../etc/passwd
```

**Resultado Esperado:**
- ✅ Backend retorna 400/403
- ✅ abspath() validation previene acceso

---

### Test T-5: Validación de BD (ACID)

#### Test T-5.1: Transacción Consistente
```python
# Backend test
1. Insert ProductImage
2. Intenta Insert duplicado
3. Rollback
```

**Resultado Esperado:**
- ✅ BD en estado válido
- ✅ No hay registros huérfanos

---

## ✅ Checklist Final de Deployment

- [ ] Todos los tests TC-1.x a TC-11.x pasan ✅
- [ ] Tests de performance T-10.1/T-10.2/T-10.3 ✅
- [ ] Tests técnicos T-1 a T-5 ✅
- [ ] No hay console.errors o warnings
- [ ] CORS configurado correctamente
- [ ] JWT tokens válidos
- [ ] BD migrada `product_images` table existe
- [ ] Archivos `/backend/uploads/` con permisos correctos
- [ ] Nginx/reverse proxy configurado (si aplica)
- [ ] Documentación actualizada

---

## 📊 Reporte de Bugs Encontrados

(Dejar en blanco, llenar durante QA)

| ID | Descripción | Severidad | Estado |
|----|-------------|-----------|--------|
| BUG-001 | [Ej: Canvas no redibuja en Safari] | Medium | [ABIERTO/RESUELTO] |

---

**Fecha Última Actualización:** 2024-Q1  
**Responsable QA:** [Tu nombre]  
**Versión:** 1.0
