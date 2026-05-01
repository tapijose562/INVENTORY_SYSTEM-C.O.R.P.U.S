# 📸 Guía de Guardado y Visualización de Imágenes - Inventory Corpus v2

## 🎯 Resumen de Cambios Implementados

Se han realizado los siguientes cambios para asegurar que las imágenes se guarden y muestren correctamente en la aplicación:

### 1. **Configuración del Proxy Angular** ✅
**Archivo**: `frontend/proxy.conf.json`

Se agregó soporte para servir archivos estáticos desde `/uploads/`:

```json
{
  "/api/*": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  },
  "/uploads/*": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
```

**¿Por qué?** Sin esta configuración, el navegador no podría acceder a las imágenes en `/uploads/` desde Angular.

---

### 2. **Mejoras en el Componente Products** ✅
**Archivo**: `frontend/src/app/pages/products/products.component.ts`

#### Cambios:
1. **Importación del ProductImageService**
   - Ahora inyecta `ProductImageService` para obtener las imágenes de cada producto

2. **Método `loadProductImages()` mejorado**
   ```typescript
   loadProductImages(product: Product): void {
     this.productImageService.getProductImages(product.id).subscribe({
       next: (result: any) => {
         if (result.images && result.images.length > 0) {
           // Mapear imágenes con formato correcto
           product.images = result.images.map((img: any) => ({
             id: img.id,
             url: img.image_url || img.url,  // Maneja ambos nombres de campo
             filename: img.image_filename || img.filename,
             is_primary: img.is_primary
           }));
           
           // Establecer imagen primaria si no está establecida
           if (!product.image_url && product.images.length > 0) {
             const primaryImage = product.images.find(img => img.is_primary === 1) || product.images[0];
             product.image_url = primaryImage.url;
           }
           console.log(`✅ Loaded ${result.images.length} images for product ${product.name}`);
         }
       },
       error: (error: any) => {
         console.error(`❌ Error loading images for product ${product.id}:`, error);
       }
     });
   }
   ```

3. **Método `loadProducts()` mejorado**
   - Ahora llama a `loadProductImages()` para cada producto después de cargarlos
   - Esto asegura que se cargan las imágenes asincronicamente

4. **Validación de URLs mejorada**
   ```typescript
   isValidImageUrl(url: string | undefined): boolean {
     if (!url) return false;
     const trimmed = url.trim();
     // Acepta URLs que comienzan con /, http://, o https://
     return trimmed.length > 0 && 
            !trimmed.includes('undefined') && 
            (trimmed.startsWith('/') || 
             trimmed.startsWith('http://') || 
             trimmed.startsWith('https://'));
   }
   ```

---

### 3. **Mejoras en el Componente Detection** ✅
**Archivo**: `frontend/src/app/pages/detection/detection.component.ts`

#### Cambios:
1. **Método `loadProductImages()` mejorado**
   - Mapea correctamente las propiedades de las imágenes
   - Maneja ambos nombres de campos (`image_url` o `url`)
   - Mejor logging para debugging

---

## 🔄 Flujo Completo de Guardado y Visualización

### Flujo 1: Guardando Imágenes (Detection → Backend)

```
1. Usuario sube imagen en Detection Component
   ↓
2. Detection.component.ts → productImageService.uploadBatchImages()
   ↓
3. FormData enviado a: POST /api/v1/product-images/upload-batch
   ↓
4. Backend (product_images.py):
   - Recibe archivos
   - Les asigna nombres: product_{id}_{uuid}.jpg
   - Las guarda en carpeta: /uploads/
   - Crea registros en BD: ProductImage
   - Retorna: ProductImageList con URLs
   ↓
5. Frontend recibe respuesta
   ↓
6. Se llama loadProductImages() para cargar las imágenes guardadas
```

### Flujo 2: Visualizando Imágenes (Backend → Products)

```
1. ProductsComponent.ngOnInit() → loadProducts()
   ↓
2. GET /api/v1/products (obtiene todos los productos)
   ↓
3. Para cada producto, se llama loadProductImages(product)
   ↓
4. GET /api/v1/product-images/product/{productId}
   ↓
5. Backend retorna: ProductImageList con todas las imágenes
   ↓
6. Frontend mapea las imágenes al objeto product.images[]
   ↓
7. Template HTML usa getCurrentImage(product) para mostrar la principal
   ↓
8. Las URLs se proxean a través de Angular: /uploads/product_X_uuid.jpg
   ↓
9. FastAPI sirve el archivo estático desde /uploads/
```

---

## 📋 Configuración del Backend (Ya Existe)

### Archivo: `backend/main.py`
```python
# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
```

### Archivo: `backend/app/core/config.py`
```python
UPLOAD_DIR: str = "uploads"  # Carpeta donde se guardan las imágenes
```

### Archivo: `backend/app/api/routes/product_images.py`
- Endpoint: `POST /upload-batch` - Sube múltiples imágenes
- Endpoint: `GET /product/{product_id}` - Obtiene todas las imágenes de un producto

---

## 🚀 Instrucciones para Probar

### Paso 1: Iniciar el Backend
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

Verifica que el servidor inicie sin errores y las tablas se creen.

### Paso 2: Iniciar el Frontend
```bash
cd frontend
npm install
npm start
```

Asegúrate de que `ng serve` esté usando el `proxy.conf.json`.

### Paso 3: Probar el Flujo Completo
1. Abre http://localhost:4200
2. Inicia sesión (admin/admin123)
3. Ve a **Detection** → Sube una imagen
4. Confirma los datos del producto y **Guardar**
5. Ve a **Products** → Deberías ver las imágenes del producto

---

## 🔍 Debugging / Solución de Problemas

### Las imágenes no se muestran en Products

1. **Abre la consola del navegador** (F12)
2. Ve a la pestaña **Network**
3. Recarga la página
4. Busca requests a `/uploads/product_*`
5. Si ves errores 404:
   - Verifica que el proxy.conf.json esté actualizado
   - Reinicia `ng serve`
   - Verifica que el backend esté corriendo en `http://localhost:8000`

### Script de Diagnóstico

Ejecuta este script para verificar el estado de las imágenes:
```bash
python diagnose_images.py
```

Esto mostrará:
- Archivos de imagen en la carpeta `/uploads`
- Registros de imágenes en la BD
- URLs de las imágenes guardadas
- Imágenes "huérfanas" (en BD pero no en disco)

---

## 📊 Estructura de Datos

### ProductImage (BD)
```python
{
  "id": 1,
  "product_id": 10,
  "image_url": "/uploads/product_10_abc123def.jpg",
  "image_filename": "product_10_abc123def.jpg",
  "image_size": 125000,
  "is_primary": 1,
  "status": "saved",
  "created_at": "2024-04-09T10:30:00Z",
  "updated_at": "2024-04-09T10:30:00Z"
}
```

### Product (BD) - Después de guardar imágenes
```python
{
  "id": 10,
  "name": "Nike - Rojo",
  "brand": "Nike",
  "image_url": "/uploads/product_10_abc123def.jpg",  # Imagen primaria
  "images": [  # Array de todas las imágenes
    { "id": 1, "url": "/uploads/product_10_abc123def.jpg", "is_primary": 1 },
    { "id": 2, "url": "/uploads/product_10_xyz789.jpg", "is_primary": 0 }
  ]
}
```

---

## ✅ Verificación Final

Después de implementar estos cambios, verifica que:

- [ ] `proxy.conf.json` incluye `/uploads/*` → target localhost:8000
- [ ] `ProductsComponent` inyecta `ProductImageService`
- [ ] `loadProducts()` llama a `loadProductImages()` para cada producto
- [ ] `ProductsComponent` HTML muestra `getCurrentImage(product)` 
- [ ] Backend `/uploads` está montado en `main.py`
- [ ] Las imágenes se guardan en carpeta `uploads/` en backend
- [ ] URLs de imágenes siguen el patrón `/uploads/product_ID_UUID.jpg`

---

## 📝 Notas Importantes

1. **Rutas de imágenes**: Las imágenes se sirven desde `/uploads/` que está:
   - Guardadas en disco en: `backend/uploads/`
   - Servidas por FastAPI en: `http://localhost:8000/uploads/`
   - Proxyadas desde Angular en: `http://localhost:4200/uploads/`

2. **Primary image**: La primera imagen subida se marca como `is_primary = 1`

3. **Carrusel en Products**: Si hay múltiples imágenes, el componente muestra:
   - Botones ◄ ► para navegar
   - Indicadores de página (puntos)
   - Zoom en/out disponible

4. **Manejo de errores**: Las URLs inválidas muestran "📷 No Image" placeholder

---

## 🎯 Próximos Pasos

Si después de estos cambios las imágenes aún no aparecen:

1. Ejecuta el script de diagnóstico: `python diagnose_images.py`
2. Revisa los logs de la consola del navegador (F12)
3. Verifica los requests en la pestaña Network del navegador
4. Asegúrate de que el backend está corriendo: `http://localhost:8000/health`
5. Intenta criar un nuevo producto con imágenes desde Detection
