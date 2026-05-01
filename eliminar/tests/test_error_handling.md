# Error Handling Test Plan - Detection Component

## Objetivo
Validar que el componente `detection.component.ts` maneja apropiadamente todos los tipos de errores durante la creación de productos.

## Cambios Implementados

### Frontend (detection.component.ts)
✅ Validación de campo requerido `Brand` antes de enviar al backend
✅ Valores por defecto para campos opcionales:
  - `color_rgb`: `{ r: 0, g: 0, b: 0 }`
  - `yolo_confidence`: `0.5`
  - `detected_text`: `""` (string vacío)
✅ Manejo mejorado de objetos de error:
  - Detección de errores de conexión (status === 0)
  - Parsing de err.error.detail/message
  - Fallback a err.message
  - Logging con indicadores visuales (✓, ✗)
✅ Limpieza de estados:
  - `this.loading = false` en error
  - `this.uploadingImages = false` en error

### Backend (app/schemas/__init__.py)
✅ Validador para `brand` - no puede ser vacío
✅ Validador para `name` - no puede ser vacío
✅ Todos los validadores son case-insensitive y trimean whitespace

### Backend (app/api/routes/products.py)
✅ Validación adicional de `name` y `brand` en el endpoint
✅ HTTPException con status 422 para campos requeridos faltantes
✅ Valores por defecto para campos opcionales
✅ Limpieza de valores con `.strip()`

## Test Cases

### 1. Test: Guardar producto sin seleccionar imágenes
**Entrada**: Click en "Guardar producto completo" sin imágenes
**Esperado**: Mostrar error "No hay imágenes para crear el producto"
**Validación**: ✓
```typescript
// El componente valida esto localmente
if (this.selectedFiles.length === 0) {
  this.error = 'No hay imágenes para crear el producto';
  return;
}
```

### 2. Test: Guardar producto sin resultados de detección guardados
**Entrada**: Cargar imágenes pero no guardar ningún resultado y hacer click en "Guardar producto completo"
**Esperado**: Mostrar error "Debes guardar al menos un resultado de detección antes de crear el producto"
**Validación**: ✓
```typescript
const savedCount = this.imageDetectionResults
  .filter((result: any) => result?.saved).length;
if (savedCount === 0) {
  this.error = 'Debes guardar al menos un resultado de detección...';
  return;
}
```

### 3. Test: Guardar producto sin campo "Brand"
**Entrada**: Procesar imagen, dejar campo "Brand" vacío, hacer click en "Guardar producto completo"
**Esperado**: Mostrar error "El campo \"Brand\" es requerido para crear el producto."
**Validación**: ✓ (Frontend + Backend)
```typescript
// Frontend validation
if (!baseResult.brand || baseResult.brand.trim().length === 0) {
  this.error = 'El campo "Brand" es requerido para crear el producto.';
  return;
}

// Backend validation (ProductCreate validator)
@validator('brand')
def validate_brand(cls, value):
    if not value or not value.strip():
        raise ValueError('Brand field is required and cannot be empty')
```

### 4. Test: Guardar producto con talla inválida
**Entrada**: Ingresar talla fuera de rango (ej. -5 o 60)
**Esperado**: Mostrar error "La talla debe ser un valor numérico entre 0 y 50."
**Validación**: ✓
```typescript
if (!this.isSizeValid(baseResult.size)) {
  this.error = 'La talla debe ser un valor numérico entre 0 y 50.';
  return;
}
```

### 5. Test: Guardar producto con precio inválido
**Entrada**: Ingresar precio menor a 10.000 COP
**Esperado**: Mostrar error "El precio debe ser mínimo 10.000 COP."
**Validación**: ✓
```typescript
if (baseResult.price !== null && baseResult.price !== undefined && 
    !this.isPriceValid(baseResult.price)) {
  this.error = 'El precio debe ser mínimo 10.000 COP.';
  return;
}
```

### 6. Test: Servidor sin conexión
**Entrada**: Detener backend, luego intentar guardar producto
**Esperado**: Mostrar error claro sobre conexión al servidor
**Validación**: ✓
```typescript
// Frontend
if (err.status === 0) {
  errorMsg = 'No hay conexión con el servidor. Verifica que el backend esté corriendo.';
}

// Console log
console.error('✗ Error al crear producto:', err);
```

### 7. Test: Backend rechaza por Brand vacío
**Entrada**: Enviar producto con Brand vacío (si valida frontend falla)
**Esperado**: Backend retorna HTTPException 422 con detalle claro
**Validación**: ✓
```python
@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if not product.brand or not product.brand.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Brand field is required"
        )
```

### 8. Test: Error de validación de Pydantic
**Entrada**: Enviar precio negativo o muy grande
**Esperado**: Pydantic valida y retorna error 422 con detalle
**Validación**: ✓
```python
price: Optional[float] = Field(None, ge=10000)  # ge = greater than or equal
```

### 9. Test: Objeto de error serializable
**Entrada**: Intentar crear producto que genere error en el backend
**Esperado**: No ver `{ "isTrusted": true }` en el UI
**Validación**: ✓ - Mejorado manejo en error handler
```typescript
// Diferencia entre tipos de error
if (err.error?.detail) { ... }         // String detail
else if (err.error?.message) { ... }   // Error object
else if (err.message) { ... }          // HTTP error
else if (typeof err.error === 'string') { ... }  // Raw string
```

### 10. Test: Subida de imágenes falla
**Entrada**: Criar producto pero falla la subida de imágenes
**Esperado**: Mostrar error específico de subida sin bloquear UI
**Validación**: ✓
```typescript
error: (err) => {
  this.uploadingImages = false;
  this.loading = false;  // Desbloquear UI
  console.error('✗ Error al subir imágenes:', err);
  const errorMsg = err.error?.detail || err.statusText || err.message || '...';
  this.error = 'Error al subir imágenes: ' + errorMsg;
}
```

### 11. Test: Campos con valores por defecto
**Entrada**: Crear producto sin proporcionar rgb, confidence, o detected_text
**Esperado**: Se usan valores por defecto correctamente
**Validación**: ✓
```typescript
color_rgb: baseResult.rgb || { r: 0, g: 0, b: 0 },
yolo_confidence: baseResult.confidence || 0.5,
detected_text: baseResult.text || '',
```

### 12. Test: Logging de debugging
**Entrada**: Abrir DevTools y ver logs
**Esperado**: Ver logs detallados del proceso
**Validación**: ✓
```
✓ Validaciones completadas. Enviando producto al backend: {...}
✓ Producto creado exitosamente con ID: 123
✓ Imágenes subidas exitosamente
✗ Error al crear producto: {...}
Mensaje de error final: Error al crear producto completo: ...
```

## Procedimiento de Prueba Manual

### Setup
1. Abrir terminal en `backend/` y ejecutar: `python -m uvicorn main:app --reload`
2. Abrir terminal en `frontend/` y ejecutar: `npm start`
3. Navegar a http://localhost:4200/detection
4. Loguear con credenciales válidas

### Prueba 1: Validación local de Brand
```
1. Upload multiple images
2. Click en primera imagen
3. Dejar Brand vacío
4. Click "Guardar resultado actual" - debería funcionar (local save)
5. Click "Guardar producto completo" - debería mostrar error
   ✓ Esperado: "El campo "Brand" es requerido para crear el producto."
```

### Prueba 2: Error de conexión
```
1. Detener el backend (Ctrl+C)
2. Rellenar formulario con datos válidos
3. Click "Guardar producto completo"
4. Esperar respuesta de error
   ✓ Esperado: "No hay conexión con el servidor..."
5. Verificar que UI no está bloqueada (loading spinner desaparece)
```

### Prueba 3: Error del backend
```
1. Asegurar que backend está corriendo
2. Usar un interceptor (DevTools Network > throttle) para simular error 500
3. O modificar backend para retornar error específico
4. Click "Guardar producto completo"
   ✓ Esperado: Mensaje de error legible, no "{ "isTrusted": true }"
```

### Prueba 4: Valores por defecto
```
1. Procesar imagen que no detecte color RGB ni confidence
2. Click "Guardar producto completo"
3. Abrir DevTools > Network > POST /products
4. Ver el payload enviado
   ✓ Esperado: 
     - color_rgb: { r: 0, g: 0, b: 0 }
     - yolo_confidence: 0.5
     - detected_text: ""
```

## Verificación de Compilación

### Frontend
```bash
cd frontend
npm run build
# ✓ Esperado: Build exitoso sin errores de TypeScript
```

### Backend
```bash
cd backend
python -m py_compile app/schemas/__init__.py
python -m py_compile app/api/routes/products.py
# ✓ Esperado: Sin errores de sintaxis Python
```

## Métricas de Éxito

- [ ] Todos los test cases pasan
- [ ] No hay `{ "isTrusted": true }` en errores del UI
- [ ] Loading spinner se desactiva en todos los escenarios de error
- [ ] Logs en DevTools muestran flujo claro con indicadores ✓/✗
- [ ] Mensajes de error son claros y accionables
- [ ] Backend valida campos requeridos
- [ ] Valores por defecto se aplican correctamente

## Notas de Debugging

Si aún se ve `{ "isTrusted": true }` en el error:
1. Abrir DevTools F12 > Console
2. Filtrar logs por "Error al crear producto"
3. Ver el objeto `err` completo en console.error
4. Verificar si la estructura es:
   - err.error?.detail (string)
   - err.error?.message (string)
   - err.message (string)
   - O algo diferente

Si falla la subida de imágenes:
1. Verificar que el producto se creó exitosamente (check DB)
2. Revisar logs de ProductImageService.uploadBatchImages
3. Verificar permisos de carpeta `backend/uploads/`
4. Check NetworkTab en DevTools para ver POST a /product-images/upload-batch

## Estado Actual: ✅ IMPLEMENTADO Y LISTO PARA PRUEBAS
